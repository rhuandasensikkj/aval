package com.eloeeducacao;

import android.content.Context;

public final class Ov {
    private static volatile boolean ligado;
    public static volatile boolean fixo;

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
