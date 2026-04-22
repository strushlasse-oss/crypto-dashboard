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
    <div className={cn("cp-card flex w-[132px] flex-col items-center px-3 py-3")}>
      <span className="cp-label-caps">{label}</span>
      <span
        className="mt-1 text-[13px] font-bold tracking-wide"
        style={{ color: TONE_TEXT[tone] }}
      >
        {value}
      </span>
      <div className="mt-1">
        <Gauge value={needle} size={86} thickness={7} />
      </div>
    </div>
  );
}
