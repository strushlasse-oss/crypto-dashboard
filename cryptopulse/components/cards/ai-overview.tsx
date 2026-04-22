"use client";

import { Sparkles } from "lucide-react";
import { CardShell } from "./card-shell";

type Props = { text: string; delay?: number };

export function AIOverview({ text, delay = 0 }: Props) {
  return (
    <CardShell delay={delay}>
      <div className="flex items-center gap-2">
        <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-[color:var(--accent-glow)]">
          <Sparkles className="h-3.5 w-3.5" style={{ color: "var(--accent-cp)" }} />
        </div>
        <span className="cp-label-caps" style={{ color: "var(--accent-cp)" }}>
          AI overview
        </span>
      </div>
      <p className="mt-3 text-[13.5px] leading-[1.65] text-[color:var(--text-primary)]">
        {text}
      </p>
    </CardShell>
  );
}
