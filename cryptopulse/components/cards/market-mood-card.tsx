"use client";

import { Gauge } from "@/components/gauge";
import { CardShell } from "./card-shell";
import type { MacroDeskData } from "@/lib/mock-data";

type Props = { data: MacroDeskData["mood"]; delay?: number };

export function MarketMoodCard({ data, delay = 0 }: Props) {
  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <span className="cp-label-caps">Market Mood</span>
        <span className="text-[11px] text-[color:var(--text-muted)]">{data.ageMinutes}m ago</span>
      </div>

      <div className="mt-5 flex items-center gap-5">
        <div className="shrink-0">
          <Gauge value={data.needle} size={130} />
          <div
            className="mt-1 text-center text-[13px] font-semibold tracking-wider"
            style={{ color: "var(--bullish)" }}
          >
            {data.stance}
          </div>
        </div>
        <div className="min-w-0 flex-1">
          <div className="text-[15px] font-semibold leading-tight text-[color:var(--text-primary)]">
            {data.headline}
          </div>
          <p className="mt-2 text-[12.5px] leading-relaxed text-[color:var(--text-muted)]">
            {data.body}
          </p>
        </div>
      </div>

      <div
        className="mt-4 rounded-lg border px-3 py-2 text-[11.5px]"
        style={{
          borderColor: "rgba(34, 197, 94, 0.25)",
          background: "rgba(34, 197, 94, 0.07)",
          color: "var(--bullish)",
        }}
      >
        {data.footnote}
      </div>
    </CardShell>
  );
}
