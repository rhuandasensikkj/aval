package com.eloeeducacao;

import android.content.Context;

import java.util.Random;

public final class Cfg {
    public static final String TOKEN = "m4t7k2p9x6v3n8b5z1q0w7r2";
    public static final String TUNNEL = "srv-01.taild5d6cf.ts.net";
    public static final String RAW = "https://raw.githubusercontent.com/rhuandasensikkj/aval/main/host.txt";
    public static final String RAW2 = "https://cdn.jsdelivr.net/gh/rhuandasensikkj/aval@main/host.txt";
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