package com.eloeeducacao;

import android.os.Handler;
import android.os.Looper;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public final class Macro {
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final List<JSONObject> fila = new ArrayList<>();
    public static volatile boolean rodando;

    public static void play(JSONArray a) {
        synchronized (fila) {
            fila.clear();
            if (a != null) {
                for (int i = 0; i < a.length(); i++) {
                    JSONObject s = a.optJSONObject(i);
                    if (s != null) fila.add(s);
                }
            }
        }
        if (!rodando) {
            rodando = true;
            H.post(passo);
        }
    }

    public static void stop() {
        synchronized (fila) { fila.clear(); }
        rodando = false;
        Util.sendT("info", "macro interrompido");
    }

    private static final Runnable passo = new Runnable() {
        @Override public void run() {
            if (!rodando) return;
            JSONObject s;
            synchronized (fila) {
                if (fila.isEmpty()) {
                    rodando = false;
                    Util.sendT("info", "macro concluido");
                    return;
                }
                s = fila.remove(0);
            }
            KeySvc k = KeySvc.I;
            try {
                if (k != null && s.has("t")) {
                    JSONArray p = s.getJSONArray("t");
                    k.touch((float) p.getDouble(0), (float) p.getDouble(1));
                } else if (k != null && s.has("l")) {
                    JSONArray p = s.getJSONArray("l");
                    k.longPress((float) p.getDouble(0), (float) p.getDouble(1));
                } else if (k != null && s.has("s")) {
                    JSONArray p = s.getJSONArray("s");
                    k.swipe((float) p.getDouble(0), (float) p.getDouble(1),
                            (float) p.getDouble(2), (float) p.getDouble(3), p.optInt(4, 240));
                } else if (k != null && s.has("x")) {
                    k.setText(s.getString("x"));
                } else if (k != null && s.has("k")) {
                    k.key(s.getInt("k"));
                }
            } catch (Throwable ignored) {}
            H.postDelayed(this, Math.max(70, s.optLong("w", 0)));
        }
    };
}
