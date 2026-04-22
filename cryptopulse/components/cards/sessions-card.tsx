"use client";

import { useEffect, useState } from "react";
import { CardShell } from "./card-shell";
import type { MacroDeskData } from "@/lib/mock-data";

type Props = { sessions: MacroDeskData["sessions"]; delay?: number };

function useUTCHour() {
  const [h, setH] = useState<number | null>(null);
  useEffect(() => {
    const tick = () => setH(new Date().getUTCHours() + new Date().getUTCMinutes() / 60);
    tick();
    const id = setInterval(tick, 60_000);
    return () => clearInterval(id);
  }, []);
  return h;
}

export function SessionsCard({ sessions, delay = 0 }: Props) {
  const hour = useUTCHour();

  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <div>
          <div className="cp-label-caps">Market Sessions</div>
          <div className="cp-heading-xl mt-1.5 text-[19px] text-[color:var(--text-primary)]">
            Global Trading Clock
          </div>
        </div>
        <span className="rounded-full border bg-[color:var(--bg-elevated-2)] px-2.5 py-1 text-[10px] font-medium text-[color:var(--text-muted)]">
          UTC
        </span>
      </div>

      <div className="mt-5 space-y-3">
        {sessions.map((s) => {
          const hoursArr = Array.from({ length: 24 }, (_, i) => i);
          const inRange = (i: number) => i >= s.rangeStart && i < s.rangeEnd;
          return (
            <div key={s.name}>
              <div className="mb-1.5 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-[12.5px] font-semibold text-[color:var(--text-primary)]">
                    {s.name}
                  </span>
                  <span className="text-[10.5px] text-[color:var(--text-muted)]">{s.timezone}</span>
                </div>
                <span
                  className="text-[10px] font-semibold uppercase tracking-wider"
                  style={{ color: s.active ? "var(--accent-cp)" : "var(--text-dim)" }}
                >
                  {s.active ? "Live" : "Closed"}
                </span>
              </div>
              <div className="relative flex h-5 overflow-hidden rounded-md bg-[color:var(--bg-elevated-2)]">
                {hoursArr.map((i) => (
                  <div
                    key={i}
                    className="flex-1"
                    style={{
                      background: inRange(i)
                        ? s.active
                          ? "linear-gradient(180deg, rgba(45,212,191,0.5), rgba(45,212,191,0.25))"
                          : "rgba(255,255,255,0.06)"
                        : "transparent",
                      borderRight: i < 23 ? "1px solid rgba(255,255,255,0.03)" : "none",
                    }}
                  />
                ))}
                {hour !== null && (
                  <div
                    className="pointer-events-none absolute inset-y-0 w-px bg-white/70"
                    style={{ left: `${(hour / 24) * 100}%` }}
                  />
                )}
              </div>
            </div>
          );
        })}

        <div className="mt-2 flex items-center justify-between text-[10px] text-[color:var(--text-dim)]">
          <span>00</span>
          <span>06</span>
          <span>12</span>
          <span>18</span>
          <span>24</span>
        </div>
      </div>
    </CardShell>
  );
}
