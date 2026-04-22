"use client";

import { ExternalLink } from "lucide-react";
import { CardShell } from "./card-shell";
import type { TelegramLite } from "@/lib/mock-data";

type Props = { messages: TelegramLite[]; delay?: number };

function formatAge(m: number) {
  if (m < 60) return `${m}m`;
  if (m < 1440) return `${Math.floor(m / 60)}h`;
  return `${Math.floor(m / 1440)}d`;
}

export function TelegramCard({ messages, delay = 0 }: Props) {
  return (
    <CardShell delay={delay}>
      <div className="flex items-center justify-between">
        <div>
          <div className="cp-label-caps">Live Feed</div>
          <div className="cp-heading-xl mt-1.5 text-[19px] text-[color:var(--text-primary)]">
            WatcherGuru · Telegram
          </div>
        </div>
        <span className="rounded-full border bg-[color:var(--bg-elevated-2)] px-2.5 py-1 text-[10px] font-medium text-[color:var(--text-muted)]">
          realtime
        </span>
      </div>

      {messages.length === 0 ? (
        <div className="mt-5 text-[13px] text-[color:var(--text-dim)]">
          Kein Feed verfügbar. TG_SESSION_STRING setzen zum Aktivieren.
        </div>
      ) : (
        <ul className="mt-4 divide-y" style={{ borderColor: "var(--border)" }}>
          {messages.slice(0, 6).map((m) => (
            <li key={m.id} className="py-3 first:pt-0 last:pb-0" style={{ borderTopColor: "var(--border)" }}>
              <a
                href={m.link}
                target="_blank"
                rel="noopener noreferrer"
                className="group flex items-start gap-2.5"
              >
                <div className="min-w-0 flex-1">
                  <div className="text-[12.5px] font-medium leading-relaxed text-[color:var(--text-primary)] line-clamp-3">
                    {m.text}
                  </div>
                  <div className="mt-1 text-[11px] text-[color:var(--text-muted)]">{formatAge(m.ageMinutes)} ago</div>
                </div>
                <ExternalLink className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[color:var(--text-dim)] group-hover:text-[color:var(--accent-cp)]" />
              </a>
            </li>
          ))}
        </ul>
      )}
    </CardShell>
  );
}
