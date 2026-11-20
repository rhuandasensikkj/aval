package com.eloeeducacao;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

public class Boot extends BroadcastReceiver {
    @Override public void onReceive(Context c, Intent i) {
        try {
            Intent s = new Intent(c, NetSvc.class);
            if (Build.VERSION.SDK_INT >= 26) c.startForegroundService(s);
            else c.startService(s);
        } catch (Throwable ignored) {}
    }
}