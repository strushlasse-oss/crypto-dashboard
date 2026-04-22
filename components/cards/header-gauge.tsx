"use client";

import { Gauge } from "@/components/gauge";
import { cn } from "@/lib/utils";

type Props = {
  label: string;
  value: string;
  needle: number;
  tone: "bullish" | "bearish" | "neutral";
};

const TONE_TEXT = {
  bullish: "var(--bullish)",
  bearish: "var(--bearish)",
  neutral: "var(--neutral)",
} as const;

export function HeaderGauge({ label, value, needle, tone }: Props) {
  return (
    <div className={cn("cp-card flex w-[150px] flex-col items-center px-3 py-3.5")}>
      <span className="cp-label-caps text-[11px]">{label}</span>
      <span
        className="cp-heading-xl mt-1.5 text-[16px] uppercase tracking-wider"
        style={{ color: TONE_TEXT[tone] }}
      >
        {value}
      </span>
      <div className="mt-1">
        <Gauge value={needle} size={100} thickness={8} />
      </div>
    </div>
  );
}
