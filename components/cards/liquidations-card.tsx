"use client";

import { CardShell } from "./card-shell";
import type { LiquidationLite } from "@/lib/mock-data";

type Props = { rows: LiquidationLite[]; delay?: number };

export function LiquidationsCard({ rows, delay = 0 }: Props) {
  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <div>
          <div className="cp-label-caps">Liquidation Pressure</div>
          <div className="cp-heading-xl mt-1.5 text-[19px] text-[color:var(--text-primary)]">
            Long / Short Balance
          </div>
        </div>
        <span className="rounded-full border bg-[color:var(--bg-elevated-2)] px-2.5 py-1 text-[10px] font-medium text-[color:var(--text-muted)]">
          Binance · 1h
        </span>
      </div>

      {rows.length === 0 ? (
        <div className="mt-5 text-[13px] text-[color:var(--text-dim)]">Keine Daten.</div>
      ) : (
        <div className="mt-5 space-y-4">
          {rows.map((r) => {
            const oiColor =
              r.oiChangePct == null ? "var(--text-dim)" :
              r.oiChangePct > 0 ? "var(--bullish)" : "var(--bearish)";
            const pressureColor =
              r.pressure === "longs" ? "var(--bearish)" :
              r.pressure === "shorts" ? "var(--bullish)" :
                                        "var(--text-muted)";
            return (
              <div key={r.coinId}>
                <div className="mb-1.5 flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="cp-heading-xl text-[14px] uppercase text-[color:var(--text-primary)]">{r.symbol}</span>
                    <span className="text-[11px] text-[color:var(--text-muted)]">L/S {r.lsRatio.toFixed(2)}</span>
                  </div>
                  <div className="flex items-center gap-3 text-[11px]">
                    <span style={{ color: oiColor }}>
                      OI {r.oiChangePct == null ? "–" : `${r.oiChangePct >= 0 ? "+" : ""}${r.oiChangePct.toFixed(2)}%`}
                    </span>
                    <span
                      className="cp-heading-xl uppercase tracking-wider"
                      style={{ color: pressureColor }}
                    >
                      {r.pressure === "neutral" ? "balanced" : `${r.pressure} liq.`}
                    </span>
                  </div>
                </div>
                <div className="flex h-3 overflow-hidden rounded-full bg-[color:var(--bg-elevated-2)]">
                  <div style={{ width: `${r.longPct}%`, background: "var(--bullish)" }} />
                  <div style={{ width: `${r.shortPct}%`, background: "var(--bearish)" }} />
                </div>
                <div className="mt-1 flex justify-between text-[10.5px] text-[color:var(--text-muted)]">
                  <span>Long {r.longPct.toFixed(1)}%</span>
                  <span>Short {r.shortPct.toFixed(1)}%</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </CardShell>
  );
}
