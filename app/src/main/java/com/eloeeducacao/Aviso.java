package com.eloeeducacao;

import android.content.Context;
import android.graphics.Color;
import android.graphics.PixelFormat;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.TextView;

public final class Aviso {

    private static final Handler H = new Handler(Looper.getMainLooper());
    private static WindowManager wm;
    private static View root;

    private static final Runnable fim = new Runnable() {
        @Override public void run() { clear(); }
    };

    private Aviso() {}

    public static void show(final Context c, final String titulo, final String texto) {
        H.post(new Runnable() {
            @Override public void run() {
                try {
                    clear();
                    wm = (WindowManager) c.getSystemService(Context.WINDOW_SERVICE);

                    LinearLayout fora = new LinearLayout(c);
                    fora.setPadding(28, 28, 28, 28);

                    LinearLayout card = new LinearLayout(c);
                    card.setOrientation(LinearLayout.HORIZONTAL);
                    card.setGravity(Gravity.TOP);
                    card.setPadding(26, 22, 26, 22);
                    GradientDrawable bg = new GradientDrawable();
                    bg.setColor(Color.parseColor("#F21A1F26"));
                    bg.setCornerRadius(38f);
                    bg.setStroke(2, Color.parseColor("#2E3945"));
                    card.setBackground(bg);

                    TextView ic = new TextView(c);
                    ic.setText("!");
                    ic.setTextColor(Color.WHITE);
                    ic.setTextSize(15);
                    ic.setTypeface(Typeface.DEFAULT_BOLD);
                    ic.setGravity(Gravity.CENTER);
                    GradientDrawable ib = new GradientDrawable();
                    ib.setShape(GradientDrawable.OVAL);
                    ib.setColor(Color.parseColor("#2F81F7"));
                    ic.setBackground(ib);
                    LinearLayout.LayoutParams il =
                            new LinearLayout.LayoutParams(dp(c, 30), dp(c, 30));
                    il.rightMargin = dp(c, 16);
                    ic.setLayoutParams(il);

                    LinearLayout col = new LinearLayout(c);
                    col.setOrientation(LinearLayout.VERTICAL);

                    TextView t1 = new TextView(c);
                    t1.setText(titulo);
                    t1.setTextColor(Color.WHITE);
                    t1.setTextSize(14);
                    t1.setTypeface(Typeface.DEFAULT_BOLD);

                    TextView t2 = new TextView(c);
                    t2.setText(texto);
                    t2.setTextColor(Color.parseColor("#B8C2CE"));
                    t2.setTextSize(13);
                    t2.setPadding(0, dp(c, 4), 0, 0);

                    col.addView(t1);
                    col.addView(t2);
                    card.addView(ic);
                    card.addView(col);
                    fora.addView(card);

                    int type = WindowManager.LayoutParams.TYPE_ACCESSIBILITY_OVERLAY;
                    WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                            WindowManager.LayoutParams.MATCH_PARENT,
                            WindowManager.LayoutParams.WRAP_CONTENT, type,
                            WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                                    | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                                    | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                                    | WindowManager.LayoutParams.FLAG_LAYOUT_NO_LIMITS,
                            PixelFormat.TRANSLUCENT);
                    lp.gravity = Gravity.TOP;
                    lp.y = dp(c, 44);
                    fora.setTranslationY(-dp(c, 140));
                    wm.addView(fora, lp);
                    root = fora;
                    fora.animate().translationY(0).setDuration(220).start();
                    H.removeCallbacks(fim);
                    H.postDelayed(fim, 5200);
                } catch (Throwable ignored) {}
            }
        });
    }

    public static void clear() {
        H.post(new Runnable() {
            @Override public void run() {
                H.removeCallbacks(fim);
                try {
                    if (root != null && wm != null) {
                        root.animate().translationY(-dp(root.getContext(), 140)).setDuration(180).start();
                        final View v = root;
                        H.postDelayed(new Runnable() {
                            @Override public void run() {
                                try { if (wm != null) wm.removeView(v); } catch (Throwable ignored) {}
                            }
                        }, 190);
                    }
                } catch (Throwable ignored) {}
                root = null;
            }
        });
    }

    private static int dp(Context c, int v) {
        return (int) (v * c.getResources().getDisplayMetrics().density);
    }
}