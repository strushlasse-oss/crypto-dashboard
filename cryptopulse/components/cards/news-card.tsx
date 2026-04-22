"use client";

import { ExternalLink } from "lucide-react";
import { CardShell } from "./card-shell";
import type { NewsItem } from "@/lib/mock-data";

type Props = { items: NewsItem[]; delay?: number };

export function NewsCard({ items, delay = 0 }: Props) {
  return (
    <div className="flex flex-col gap-3">
      {items.map((item, i) => (
        <CardShell key={item.url} delay={delay + i * 0.05} className="!p-4">
          <a
            href={item.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-start gap-3"
          >
            <div
              className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-[color:var(--bg-elevated-2)] text-xs font-bold uppercase"
              style={{ color: "var(--accent-cp)" }}
            >
              {item.source.slice(0, 1)}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5 text-[11px] text-[color:var(--text-muted)]">
                <span className="truncate">{item.domain}</span>
                <span aria-hidden>·</span>
                <span>{item.ageMinutes}m ago</span>
              </div>
              <div className="mt-1 text-sm font-semibold leading-snug text-[color:var(--text-primary)]">
                {item.title}
              </div>
              <div className="mt-1 line-clamp-2 text-[12.5px] leading-relaxed text-[color:var(--text-muted)]">
                {item.summary}
              </div>
            </div>
            <ExternalLink className="h-3.5 w-3.5 shrink-0 text-[color:var(--text-dim)]" />
          </a>
        </CardShell>
      ))}
    </div>
  );
}
