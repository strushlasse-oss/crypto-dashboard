"use client";

import { Feather } from "lucide-react";
import { CardShell } from "./card-shell";
import type { MacroDeskData } from "@/lib/mock-data";

type Props = { data: MacroDeskData["policy"]; delay?: number };

export function MarketPolicyCard({ data, delay = 0 }: Props) {
  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <span className="cp-label-caps">Market Policy</span>
        <span className="text-[11px] text-[color:var(--text-muted)]">{data.ageMinutes}m ago</span>
      </div>

      <div className="mt-5 flex items-center gap-5">
        <div className="flex shrink-0 flex-col items-center" style={{ width: 130 }}>
          <div
            className="flex h-[72px] w-[72px] items-center justify-center rounded-full"
            style={{
              background: "radial-gradient(circle, rgba(45,212,191,0.25) 0%, rgba(45,212,191,0.02) 70%)",
            }}
          >
            <Feather
              className="h-[52px] w-[52px]"
              style={{
                color: "var(--accent-cp)",
                filter: "drop-shadow(0 0 12px rgba(45,212,191,0.4))",
              }}
              strokeWidth={1.2}
            />
          </div>
          <div
            className="mt-3 text-[13px] font-semibold tracking-[0.18em]"
            style={{ color: "var(--accent-cp)" }}
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
          borderColor: "rgba(45, 212, 191, 0.25)",
          background: "rgba(45, 212, 191, 0.07)",
          color: "var(--accent-cp)",
        }}
      >
        {data.footnote}
      </div>
    </CardShell>
  );
}
