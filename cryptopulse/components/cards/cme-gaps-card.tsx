"use client";

import { CardShell } from "./card-shell";
import type { CmeGap } from "@/lib/mock-data";
import { formatUsd } from "@/lib/utils";

type Props = { gaps: CmeGap[]; price: number; delay?: number };

export function CmeGapsCard({ gaps, price, delay = 0 }: Props) {
  const above = gaps.filter((g) => g.low > price).slice(0, 4);
  const below = gaps.filter((g) => g.high <= price).slice(0, 4);

  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <div>
          <div className="cp-label-caps">CME Gaps</div>
          <div className="mt-1 text-[15px] font-semibold text-[color:var(--text-primary)]">
            Unfilled Weekend Gaps · BTC Futures
          </div>
        </div>
        <span className="rounded-full border bg-[color:var(--bg-elevated-2)] px-2.5 py-1 text-[10px] font-medium text-[color:var(--text-muted)]">
          Yahoo · BTC=F
        </span>
      </div>

      {gaps.length === 0 ? (
        <div className="mt-5 text-[13px] text-[color:var(--text-dim)]">
          Keine offenen CME Gaps gefunden.
        </div>
      ) : (
        <>
          <table className="mt-4 w-full border-collapse text-[12.5px]">
            <thead>
              <tr className="border-b" style={{ borderColor: "var(--border)" }}>
                <th className="cp-label-caps py-1.5 text-left">Range</th>
                <th className="cp-label-caps py-1.5 text-left">Distance</th>
                <th className="cp-label-caps py-1.5 text-left">Gap · Date</th>
              </tr>
            </thead>
            <tbody>
              {above.map((g, i) => {
                const dist = ((g.low - price) / price) * 100;
                return (
                  <tr key={`a-${i}`}>
                    <td className="mono py-2 pr-3 font-semibold tabular">
                      {formatUsd(g.low, { decimals: 0 })}–{formatUsd(g.high, { decimals: 0 })}
                    </td>
                    <td className="py-2 pr-3 text-[11.5px]" style={{ color: "var(--bearish)" }}>
                      ▲ +{dist.toFixed(1)}% above
                    </td>
                    <td className="py-2 text-[11.5px] text-[color:var(--text-muted)]">
                      {g.sizePct >= 0 ? "+" : ""}{g.sizePct.toFixed(2)}% · {g.date}
                    </td>
                  </tr>
                );
              })}
              {below.map((g, i) => {
                const dist = ((price - g.high) / price) * 100;
                return (
                  <tr key={`b-${i}`}>
                    <td className="mono py-2 pr-3 font-semibold tabular">
                      {formatUsd(g.low, { decimals: 0 })}–{formatUsd(g.high, { decimals: 0 })}
                    </td>
                    <td className="py-2 pr-3 text-[11.5px]" style={{ color: "var(--bullish)" }}>
                      ▼ -{dist.toFixed(1)}% below
                    </td>
                    <td className="py-2 text-[11.5px] text-[color:var(--text-muted)]">
                      {g.sizePct >= 0 ? "+" : ""}{g.sizePct.toFixed(2)}% · {g.date}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div className="mt-3 text-[11px] text-[color:var(--text-dim)]">
            {above.length} above price · {below.length} below · Fill targets when price revisits the range.
          </div>
        </>
      )}
    </CardShell>
  );
}
