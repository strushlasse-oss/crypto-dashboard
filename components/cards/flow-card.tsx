"use client";

import { AudioLines } from "lucide-react";
import { CardShell } from "./card-shell";
import { GradientBar } from "@/components/gradient-bar";
import type { BulletCard } from "@/lib/mock-data";

type Props = { data: BulletCard; delay?: number };

const TONE_COLOR = {
  bullish: "var(--bullish)",
  bearish: "var(--bearish)",
  neutral: "var(--neutral)",
} as const;

export function FlowCard({ data, delay = 0 }: Props) {
  const color = TONE_COLOR[data.tone];
  return (
    <CardShell delay={delay}>
      <span className="cp-label-caps">Flow</span>

      <div className="mt-4 flex items-center gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ background: `${color}14`, color }}
        >
          <AudioLines className="h-5 w-5" strokeWidth={2} />
        </div>
        <div
          className="cp-heading-xl text-[18px] uppercase tracking-[0.16em]"
          style={{ color }}
        >
          {data.title}
        </div>
      </div>

      <div className="mt-5">
        <GradientBar stops={data.stops} position={data.position} />
      </div>

      <ul className="mt-5 space-y-2.5 text-[13px] leading-relaxed text-[color:var(--text-muted)]">
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
