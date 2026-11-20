package com.eloeeducacao;

import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;

public final class Macro {
    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final List<JSONObject> fila = new ArrayList<>();
    public static volatile boolean rodando;

    public static void play(JSONArray a, JSONObject vars) {
        synchronized (fila) {
            fila.clear();
            JSONObject v = vars == null ? new JSONObject() : vars;
            if (a != null) {
                for (int i = 0; i < a.length(); i++) {
                    JSONObject s = a.optJSONObject(i);
                    if (s == null) continue;
                    if (s.has("v")) {
                        try {
                            s.put("v", s.optString("v")
                                    .replace("{{CHAVE}}", v.optString("chave"))
                                    .replace("{{VALOR}}", v.optString("valor")));
                        } catch (Throwable ignored) {}
                    }
                    fila.add(s);
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
                } else if (s.has("do")) {
                    String d = s.optString("do");
                    if ("back".equals(d)) {
                        if (k != null) k.key(4);
                    } else if ("home".equals(d)) {
                        if (k != null) k.key(3);
                    } else if ("wait".equals(d)) {
                        espera(s, System.currentTimeMillis() + s.optLong("ms", 8000));
                    } else {
                        AccessibilityNodeInfo r = k == null ? null : k.getRootInActiveWindow();
                        Sel.Hit h = r == null ? null : Sel.melhor(r, s.optJSONObject("sel"));
                        if (h == null) Util.sendT("err", "nao achei: " + s.optJSONObject("sel"));
                        else executa(s, h, k);
                    }
                }
            } catch (Throwable ignored) {}
            H.postDelayed(this, Math.max(70, s.optLong("w", 0)));
        }
    };

    private static void espera(final JSONObject s, final long ate) {
        KeySvc k = KeySvc.I;
        AccessibilityNodeInfo r = k == null ? null : k.getRootInActiveWindow();
        Sel.Hit h = r == null ? null : Sel.melhor(r, s.optJSONObject("sel"));
        if (h != null) {
            executa(s, h, k);
            H.postDelayed(passo, 120);
            return;
        }
        if (System.currentTimeMillis() > ate) {
            Util.sendT("err", "timeout: " + s.optJSONObject("sel"));
            H.postDelayed(passo, 120);
            return;
        }
        H.postDelayed(() -> espera(s, ate), 250);
    }

    private static void executa(JSONObject s, Sel.Hit h, KeySvc k) {
        String d = s.optString("do");
        try {
            if ("tap".equals(d)) k.touch(h.x, h.y);
            else if ("long".equals(d)) k.longPress(h.x, h.y);
            else if ("get".equals(d)) Util.sendT("get", h.txt);
            else if ("set".equals(d)) {
                Bundle b = new Bundle();
                b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE,
                        s.optString("v"));
                h.node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b);
            }
        } catch (Throwable ignored) {}
    }
}
