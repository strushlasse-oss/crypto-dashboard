"use client";

import { Sparkles } from "lucide-react";
import { CardShell } from "./card-shell";

type Props = { text: string; delay?: number };

export function AIOverview({ text, delay = 0 }: Props) {
  return (
    <CardShell delay={delay}>
      <div className="flex items-center gap-2.5">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[color:var(--accent-glow)]">
          <Sparkles className="h-4 w-4" style={{ color: "var(--accent-cp)" }} />
        </div>
        <span className="cp-label-caps text-[13px]" style={{ color: "var(--accent-cp)" }}>
          AI overview
        </span>
      </div>
      <p className="mt-3.5 text-[15px] leading-[1.6] text-[color:var(--text-primary)]">
        {text}
      </p>
    </CardShell>
  );
}
