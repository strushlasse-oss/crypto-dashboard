"use client";

import { Gauge } from "@/components/gauge";
import { CardShell } from "./card-shell";

type Props = {
  value: number | null;
  classification: string | null;
  delay?: number;
};

function colorFor(v: number) {
  if (v >= 75) return "var(--bullish)";
  if (v >= 55) return "var(--bullish)";
  if (v >= 45) return "var(--neutral)";
  if (v >= 25) return "var(--bearish)";
  return "var(--bearish)";
}

export function FearGreedCard({ value, classification, delay = 0 }: Props) {
  const v = value ?? 0;
  const color = value != null ? colorFor(v) : "var(--text-dim)";

  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <span className="cp-label-caps">Fear & Greed</span>
        <span className="rounded-full border bg-[color:var(--bg-elevated-2)] px-2.5 py-1 text-[10px] font-medium text-[color:var(--text-muted)]">
          alternative.me
        </span>
      </div>

      {value == null ? (
        <div className="mt-5 text-[13px] text-[color:var(--text-dim)]">Keine Daten.</div>
      ) : (
        <div className="mt-4 flex items-center gap-5">
          <Gauge value={v} size={140} />
          <div>
            <div className="mono text-[38px] font-bold tabular leading-none" style={{ color }}>
              {v}
            </div>
            <div
              className="cp-heading-xl mt-2 text-[16px] uppercase tracking-wider"
              style={{ color }}
            >
              {classification ?? ""}
            </div>
          </div>
        </div>
      )}
    </CardShell>
  );
}
