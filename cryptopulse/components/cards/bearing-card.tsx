"use client";

import { Activity } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { CardShell } from "./card-shell";
import type { MacroDeskData } from "@/lib/mock-data";

type Props = { data: MacroDeskData["bearing"]; delay?: number };

const TONE_COLOR = {
  bullish: "var(--bullish)",
  bearish: "var(--bearish)",
  neutral: "var(--neutral)",
} as const;

export function BearingCard({ data, delay = 0 }: Props) {
  const color = TONE_COLOR[data.tone];
  const chart = data.spark.map((p, i) => ({ i, v: p }));

  return (
    <CardShell delay={delay}>
      <span className="cp-label-caps">Bearing</span>

      <div className="mt-4 flex items-center gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ background: `${color}14`, color }}
        >
          <Activity className="h-5 w-5" strokeWidth={2} />
        </div>
        <div className="text-[15px] font-bold tracking-[0.14em]" style={{ color }}>
          {data.title}
        </div>
      </div>

      <div className="mt-4 h-16 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chart} margin={{ top: 2, right: 0, bottom: 2, left: 0 }}>
            <defs>
              <linearGradient id="bearingFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.35} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke={color}
              strokeWidth={1.6}
              fill="url(#bearingFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <ul className="mt-4 space-y-2 text-[12.5px] leading-relaxed text-[color:var(--text-muted)]">
        {data.bullets.map((b, i) => (
          <li key={i} className="flex gap-2">
            <span aria-hidden style={{ color }}>
              •
            </span>
            <span>{b}</span>
          </li>
        ))}
      </ul>
    </CardShell>
  );
}
