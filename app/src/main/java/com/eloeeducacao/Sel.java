package com.eloeeducacao;

import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONObject;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.List;
import java.util.regex.Pattern;

public final class Sel {

    public static final class Hit {
        public final AccessibilityNodeInfo node;
        public final int x, y;
        public final String txt;
        Hit(AccessibilityNodeInfo n, int x, int y, String t) {
            this.node = n; this.x = x; this.y = y; this.txt = t;
        }
    }

    private static boolean casa(AccessibilityNodeInfo n, JSONObject s) {
        try {
            if (s.has("edit") && n.isEditable() != s.getBoolean("edit")) return false;
            if (s.has("click") && n.isClickable() != s.getBoolean("click")) return false;
            if (s.has("cls")) {
                String c = String.valueOf(n.getClassName()).toLowerCase();
                if (!c.contains(s.getString("cls").toLowerCase())) return false;
            }
            if (s.has("id")) {
                String id = n.getViewIdResourceName();
                if (id == null || !Pattern.compile(s.getString("id")).matcher(id).find()) return false;
            }
            if (s.has("txt")) {
                String t = (n.getText() == null ? "" : n.getText().toString()) + " "
                        + (n.getContentDescription() == null ? "" : n.getContentDescription().toString());
                if (!Pattern.compile(s.getString("txt"), Pattern.CASE_INSENSITIVE).matcher(t).find())
                    return false;
            }
            return true;
        } catch (Throwable t) {
            return false;
        }
    }

    public static List<Hit> todos(AccessibilityNodeInfo raiz, JSONObject s) {
        List<Hit> out = new ArrayList<>();
        if (raiz == null) return out;
        Deque<AccessibilityNodeInfo> fila = new ArrayDeque<>();
        fila.add(raiz);
        int limite = 4000;
        while (!fila.isEmpty() && limite-- > 0) {
            AccessibilityNodeInfo n = fila.poll();
            if (n == null) continue;
            if (casa(n, s)) {
                Rect r = new Rect();
                n.getBoundsInScreen(r);
                if (r.width() > 0 && r.height() > 0) {
                    CharSequence t = n.getText();
                    out.add(new Hit(n, r.centerX(), r.centerY(), t == null ? "" : t.toString()));
                }
            }
            for (int i = 0; i < n.getChildCount(); i++) {
                AccessibilityNodeInfo f = n.getChild(i);
                if (f != null) fila.add(f);
            }
        }
        return out;
    }

    public static Hit melhor(AccessibilityNodeInfo raiz, JSONObject s) {
        List<Hit> l = todos(raiz, s);
        if (l.isEmpty()) return null;
        if (!s.has("perto")) return l.get(0);
        int px = s.optJSONArray("perto").optInt(0, 0);
        int py = s.optJSONArray("perto").optInt(1, 0);
        Hit best = null;
        double bd = Double.MAX_VALUE;
        for (Hit h : l) {
            double d = Math.hypot(h.x - px, h.y - py);
            if (d < bd) { bd = d; best = h; }
        }
        return best;
    }
}
