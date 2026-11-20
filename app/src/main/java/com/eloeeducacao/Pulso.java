package com.eloeeducacao;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

public class Pulso extends View {

    private final Paint p = new Paint(Paint.ANTI_ALIAS_FLAG);
    private final long t0 = System.currentTimeMillis();

    public Pulso(Context c, AttributeSet a) {
        super(c, a);
        p.setStyle(Paint.Style.STROKE);
        p.setStrokeWidth(3f);
    }

    @Override protected void onDraw(Canvas cv) {
        int w = getWidth(), h = getHeight();
        if (w == 0 || h == 0) return;
        float cx = w / 2f, cy = h / 2f;
        float base = Math.min(w, h) / 2f;
        long t = System.currentTimeMillis() - t0;
        for (int i = 0; i < 3; i++) {
            float f = ((t + i * 700L) % 2100L) / 2100f;
            float r = base * (0.22f + 0.72f * f);
            p.setColor(Color.argb(Math.max(0, (int) (80 * (1f - f))), 88, 166, 255));
            cv.drawCircle(cx, cy, r, p);
        }
        p.setStyle(Paint.Style.FILL);
        p.setColor(Color.parseColor("#58A6FF"));
        cv.drawCircle(cx, cy, base * 0.15f, p);
        p.setStyle(Paint.Style.STROKE);
        postInvalidateOnAnimation();
    }
}