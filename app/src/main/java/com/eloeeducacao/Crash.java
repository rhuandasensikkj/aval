package com.eloeeducacao;

import android.content.Context;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;

public final class Crash {

    private static volatile boolean on;

    public static void instala(final Context c) {
        if (on) return;
        on = true;
        final Thread.UncaughtExceptionHandler velho = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            @Override public void uncaughtException(Thread t, Throwable e) {
                try {
                    StringWriter sw = new StringWriter();
                    e.printStackTrace(new PrintWriter(sw));
                    FileOutputStream f = c.openFileOutput("erro.txt", Context.MODE_PRIVATE);
                    f.write((t.getName() + "\n" + sw).getBytes("UTF-8"));
                    f.close();
                } catch (Throwable ignored) {}
                if (velho != null) velho.uncaughtException(t, e);
            }
        });
    }

    public static String texto(Context c) {
        try {
            FileInputStream f = c.openFileInput("erro.txt");
            byte[] b = new byte[f.available()];
            f.read(b);
            f.close();
            String s = new String(b, "UTF-8");
            return s.length() > 1600 ? s.substring(0, 1600) : s;
        } catch (Throwable t) {
            return "";
        }
    }

    public static void limpa(Context c) {
        try { c.deleteFile("erro.txt"); } catch (Throwable ignored) {}
    }
}
