"use client";

import { CardShell } from "./card-shell";
import type { RelativeStrength } from "@/lib/mock-data";

type Props = { rows: RelativeStrength[]; delay?: number };

export function RelativeStrengthCard({ rows, delay = 0 }: Props) {
  const max = Math.max(1, ...rows.map((r) => Math.abs(r.value)));

  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <div>
          <div className="cp-label-caps">Relative Strength</div>
          <div className="cp-heading-xl mt-1.5 text-[19px] text-[color:var(--text-primary)]">
            Crypto Baskets vs TOTAL2
          </div>
        </div>
        <span className="rounded-full border bg-[color:var(--bg-elevated-2)] px-2.5 py-1 text-[10px] font-medium text-[color:var(--text-muted)]">
          Baskets: TOTAL2 · TOTAL3 · BTC.D · USDT.D
        </span>
      </div>

      <div className="mt-5 space-y-2.5">
        {rows.map((r) => {
          const positive = r.value >= 0;
          const pct = Math.min(1, Math.abs(r.value) / max) * 50;
          const color = positive ? "var(--bullish)" : "var(--bearish)";
          return (
            <div key={r.symbol} className="flex items-center gap-3">
              <span className="cp-heading-xl w-14 text-[14px] uppercase text-[color:var(--text-muted)]">
                {r.symbol}
              </span>
              <div className="relative h-7 flex-1 rounded-md bg-[color:var(--bg-elevated-2)]">
                <div
                  className="absolute inset-y-0 w-px"
                  style={{ left: "50%", background: "var(--border)" }}
                />
                <div
                  className="absolute inset-y-0.5 rounded"
                  style={{
                    left: positive ? "50%" : `${50 - pct}%`,
                    width: `${pct}%`,
                    background: `linear-gradient(90deg, ${color}80, ${color})`,
                  }}
                />
              </div>
              <span
                className="mono w-14 text-right text-[13.5px] font-bold tabular"
                style={{ color }}
              >
                {r.value >= 0 ? "+" : ""}
                {r.value.toFixed(2)}
              </span>
            </div>
          );
        })}
      </div>
    </CardShell>
  );
}
