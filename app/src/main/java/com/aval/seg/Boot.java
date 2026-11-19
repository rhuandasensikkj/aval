package com.aval.seg;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

public class Boot extends BroadcastReceiver {
    @Override public void onReceive(Context c, Intent i) {
        try { Net.start(c); } catch (Throwable ignored) {}
    }
}
