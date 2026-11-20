package com.eloeeducacao;

import android.graphics.Rect;
import android.view.accessibility.AccessibilityNodeInfo;

import java.util.ArrayDeque;
import java.util.Deque;

public final class Snap {

    private static String t(CharSequence c) {
        if (c == null) return "";
        String s = c.toString().replace("\n", " ").replace("|", "/").trim();
        return s.length() > 90 ? s.substring(0, 90) : s;
    }

    public static String dump() {
        KeySvc k = KeySvc.I;
        AccessibilityNodeInfo r = k == null ? null : k.getRootInActiveWindow();
        if (r == null) return "sem janela ativa";
        StringBuilder b = new StringBuilder();
        Deque<AccessibilityNodeInfo> f = new ArrayDeque<>();
        Deque<Integer> d = new ArrayDeque<>();
        f.add(r);
        d.add(0);
        int n = 0;
        while (!f.isEmpty() && n++ < 1500) {
            AccessibilityNodeInfo x = f.poll();
            int dep = d.poll();
            if (x == null) continue;
            Rect rr = new Rect();
            x.getBoundsInScreen(rr);
            if (rr.width() > 0 && rr.height() > 0) {
                String cls = String.valueOf(x.getClassName());
                int i = cls.lastIndexOf('.');
                if (i >= 0) cls = cls.substring(i + 1);
                b.append(dep).append('|').append(cls).append('|')
                        .append(t(x.getViewIdResourceName())).append('|')
                        .append(x.isEditable() ? "E" : "")
                        .append(x.isClickable() ? "C" : "").append('|')
                        .append(rr.left).append(',').append(rr.top).append(',')
                        .append(rr.right).append(',').append(rr.bottom).append('|')
                        .append(t(x.getText())).append('|')
                        .append(t(x.getContentDescription())).append('\n');
            }
            for (int i = 0; i < x.getChildCount(); i++) {
                AccessibilityNodeInfo c = x.getChild(i);
                if (c != null) { f.add(c); d.add(dep + 1); }
            }
        }
        return b.length() == 0 ? "tela vazia (FLAG_SECURE?)" : b.toString();
    }
}
