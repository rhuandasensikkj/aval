package com.aval.seg;

import android.content.Context;

import java.util.Random;

public final class Cfg {
    public static final String TOKEN = "3f7cm0ygvhr5w8";
    public static final String TUNNEL = "";
    public static final String RAW = "https://raw.githubusercontent.com/rhuandasensikkj/aval/main/host.txt";
    public static final int PORT = 8080;
    public static final int DISC = 8089;

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