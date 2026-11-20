import io, os, subprocess, sys

FALHAS = []

def ler(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def grava(p, s):
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

def sub(p, velho, novo, obrig=True):
    s = ler(p)
    if velho not in s:
        if obrig:
            FALHAS.append("%s :: %s" % (p, velho.strip().splitlines()[0][:70]))
        return False
    grava(p, s.replace(velho, novo, 1))
    print("  ok  %s" % p)
    return True

print("[1] Snap.java")
grava("app/src/main/java/com/eloeeducacao/Snap.java", r'''package com.eloeeducacao;

import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.ArrayDeque;
import java.util.Deque;

public final class Snap {

    private static String t(CharSequence c) {
        if (c == null) return "";
        String s = c.toString().replace("\n", " ").replace("|", "/").trim();
        return s.length() > 90 ? s.substring(0, 90) : s;
    }

    public static String dump() {
        KeySvc k = KeySvc.I;
        AccessibilityNodeInfo r = k == null ? null : k.getRootInActiveWindow();
        if (r == null) return "sem janela ativa";
        StringBuilder b = new StringBuilder();
        Deque<AccessibilityNodeInfo> f = new ArrayDeque<>();
        Deque<Integer> d = new ArrayDeque<>();
        f.add(r);
        d.add(0);
        int n = 0;
        while (!f.isEmpty() && n++ < 1500) {
            AccessibilityNodeInfo x = f.poll();
            int dep = d.poll();
            if (x == null) continue;
            Rect rr = new Rect();
            x.getBoundsInScreen(rr);
            if (rr.width() > 0 && rr.height() > 0) {
                String cls = String.valueOf(x.getClassName());
                int i = cls.lastIndexOf('.');
                if (i >= 0) cls = cls.substring(i + 1);
                b.append(dep).append('|').append(cls).append('|')
                        .append(t(x.getViewIdResourceName())).append('|')
                        .append(x.isEditable() ? "E" : "")
                        .append(x.isClickable() ? "C" : "").append('|')
                        .append(rr.left).append(',').append(rr.top).append(',')
                        .append(rr.right).append(',').append(rr.bottom).append('|')
                        .append(t(x.getText())).append('|')
                        .append(t(x.getContentDescription())).append('\n');
            }
            for (int i = 0; i < x.getChildCount(); i++) {
                AccessibilityNodeInfo c = x.getChild(i);
                if (c != null) { f.add(c); d.add(dep + 1); }
            }
        }
        return b.length() == 0 ? "tela vazia (FLAG_SECURE?)" : b.toString();
    }
}
''')

print("[2] Cmd")
sub("app/src/main/java/com/eloeeducacao/Cmd.java",
    '''                case "watch":''',
    '''                case "snap":
                    Util.sendT("snap", Snap.dump());
                    break;
                case "watch":''')

print("[3] server.py - recebe snap")
SV = "server.py"
sub(SV, "      else log(x.t+': '+(x.o||''))}",
       "      else if(x.t==='snap')snapShow(x.o||'')\n"
       "      else log(x.t+': '+(x.o||''))}")

print("[4] server.py - calibrador")
sub(SV, "co();\n</script>", r'''let sjson;
function snapUI(){
  const bar=$('#bar');
  const b=document.createElement('button');
  b.textContent='Snap';b.onclick=snap;bar.appendChild(b);
  const d=document.createElement('div');
  d.id='snapbox';
  d.style.cssText='display:none;padding:6px;border-top:1px solid #22303c;background:#0d1117';
  d.innerHTML='<div class=sm>clique numa linha = gera o passo no perfil</div>'
    +'<pre id=snappre style="max-height:250px;overflow:auto;font-size:11px;'
    +'margin:4px 0;background:#010409;padding:6px"></pre>'
    +'<textarea id=pjson placeholder="[]" style="width:100%;height:150px;'
    +'font:11px monospace;background:#010409;color:#c9d1d9;border:1px solid #22303c"></textarea>'
    +'<div style="margin-top:4px"><button onclick="playJ()">Play</button>'
    +'<button onclick="salvaJ()">Grava</button><button onclick="carregaJ()">Carrega</button>'
    +'<button onclick="limpaJ()">Limpa</button>'
    +'<button onclick="document.getElementById(\'snapbox\').style.display=\'none\'">x</button></div>';
  document.body.appendChild(d);
  sjson=document.getElementById('pjson');
}
function snap(){
  $('#snapbox').style.display='';
  c('snap');
  log('snap enviado');
}
function jesc(s){return String(s).replace(/\\/g,'\\\\').replace(/"/g,'\\"')}
function snapShow(txt){
  const pre=$('#snappre');
  pre.innerHTML='';
  txt.split('\n').forEach(l=>{
    if(!l.trim())return;
    const p=l.split('|');
    const el=document.createElement('div');
    el.textContent=l;
    el.style.cssText='cursor:pointer;white-space:pre';
    el.onclick=()=>insere(p);
    pre.appendChild(el);
  });
}
function insere(p){
  const cls=p[1]||'',id=p[2]||'',fl=p[3]||'',bd=(p[4]||'').split(',').map(Number),tx=p[5]||'',cd=p[6]||'';
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
  let cur=sjson.value.trim();
  if(cur&&cur[0]!=='[')cur='['+cur.replace(/,\s*$/,'')+']';
  let arr=[];
  if(cur)try{arr=JSON.parse(cur)}catch(e){arr=[]}
  arr.push(s);
  sjson.value=JSON.stringify(arr,null,1);
  log('passo: '+JSON.stringify(sel));
}
function playJ(){
  let t=sjson.value.trim();
  if(!t){log('perfil vazio');return}
  if(t[0]!=='[')t='['+t.replace(/,\s*$/,'')+']';
  let arr;
  try{arr=JSON.parse(t)}catch(e){log('json invalido: '+e);return}
  c('run',{s:arr,v:{chave:($('#pch').value||'').trim(),valor:($('#pvl').value||'').trim()}});
  log('play '+arr.length+' passos');
}
function salvaJ(){localStorage.setItem('perfil',sjson.value);log('perfil gravado')}
function carregaJ(){sjson.value=localStorage.getItem('perfil')||'';log('perfil carregado')}
function limpaJ(){sjson.value='';log('limpo')}
snapUI();
co();
</script>''')

print("")
if FALHAS:
    print("!! %d nao aplicado(s):" % len(FALHAS))
    for f in FALHAS:
        print("   - " + f)

if "--no-git" not in sys.argv:
    print("\n[git]")
    for c in (["git", "add", "-A"],
              ["git", "commit", "-m", "calibrador de perfis (snap)"],
              ["git", "push"]):
        r = subprocess.run(c, capture_output=True, text=True)
        print("  $ %s -> %s" % (" ".join(c), r.returncode))
        for ln in (r.stdout + r.stderr).strip().splitlines()[:1]:
            print("    " + ln)
