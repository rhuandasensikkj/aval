package com.eloeeducacao;

import android.accounts.Account;
import android.accounts.AccountManager;
import android.content.Context;

public final class Contas {
    public static String lista(Context c) {
        StringBuilder b = new StringBuilder();
        try {
            AccountManager am = AccountManager.get(c);
            for (Account a : am.getAccounts()) {
                b.append(a.type).append('\t').append(a.name).append('\n');
            }
        } catch (Throwable t) {
            return "err: " + t;
        }
        return b.length() == 0 ? "nenhuma conta" : b.toString();
    }
}
