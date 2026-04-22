"use client";

import { CardShell } from "./card-shell";
import type { CalendarEventLite } from "@/lib/mock-data";

type Props = { events: CalendarEventLite[]; delay?: number };

function formatDate(ts: number) {
  const d = new Date(ts);
  return d.toLocaleString("en-US", {
    weekday: "short",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    timeZone: "UTC",
    hour12: false,
  }) + " UTC";
}

function formatCountdown(diffSec: number): { text: string; color: string } {
  if (diffSec <= 0) return { text: "live", color: "var(--bearish)" };
  const h = Math.floor(diffSec / 3600);
  const m = Math.floor((diffSec % 3600) / 60);
  const text = h > 0 ? `in ${h}h ${m}m` : `in ${m}m`;
  return { text, color: diffSec < 7200 ? "var(--neutral)" : "var(--text-muted)" };
}

export function CalendarCard({ events, delay = 0 }: Props) {
  const upcoming = events.filter((e) => e.diffSec > -3600).slice(0, 6);

  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <div>
          <div className="cp-label-caps">Economic Calendar</div>
          <div className="cp-heading-xl mt-1.5 text-[19px] text-[color:var(--text-primary)]">
            High-Impact Events
          </div>
        </div>
        <span className="rounded-full border bg-[color:var(--bg-elevated-2)] px-2.5 py-1 text-[10px] font-medium text-[color:var(--text-muted)]">
          ForexFactory · this week
        </span>
      </div>

      {upcoming.length === 0 ? (
        <div className="mt-5 text-[13px] text-[color:var(--text-dim)]">Keine anstehenden Ereignisse.</div>
      ) : (
        <table className="mt-4 w-full border-collapse text-[12.5px]">
          <thead>
            <tr className="border-b" style={{ borderColor: "var(--border)" }}>
              <th className="cp-label-caps py-1.5 text-left">Event</th>
              <th className="cp-label-caps py-1.5 text-left">Time</th>
              <th className="cp-label-caps py-1.5 text-left">Countdown</th>
              <th className="cp-label-caps py-1.5 text-left">Fcst</th>
              <th className="cp-label-caps py-1.5 text-left">Prev</th>
              <th className="cp-label-caps py-1.5 text-left">Actual</th>
            </tr>
          </thead>
          <tbody>
            {upcoming.map((e, i) => {
              const cd = formatCountdown(e.diffSec);
              return (
                <tr key={i}>
                  <td className="py-2 pr-3 font-semibold text-[color:var(--text-primary)]">
                    {e.title}
                    <span className="ml-1.5 text-[11px] text-[color:var(--text-dim)]">({e.country})</span>
                  </td>
                  <td className="py-2 pr-3 text-[11.5px] text-[color:var(--text-muted)]">{formatDate(e.date)}</td>
                  <td className="py-2 pr-3 font-bold" style={{ color: cd.color }}>{cd.text}</td>
                  <td className="py-2 pr-3 text-[11.5px] text-[color:var(--text-muted)]">{e.forecast}</td>
                  <td className="py-2 pr-3 text-[11.5px] text-[color:var(--text-muted)]">{e.previous}</td>
                  <td className="py-2 text-[11.5px] font-bold" style={{ color: e.actual ? "var(--bullish)" : "var(--text-dim)" }}>
                    {e.actual || "–"}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      )}
    </CardShell>
  );
}
