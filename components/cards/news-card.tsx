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
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[color:var(--bg-elevated-2)] text-[13px] font-bold uppercase"
              style={{ color: "var(--accent-cp)" }}
            >
              {item.source.slice(0, 1)}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-1.5 text-[12px] font-medium text-[color:var(--text-muted)]">
                <span className="truncate">{item.domain}</span>
                <span aria-hidden>·</span>
                <span>{item.ageMinutes}m ago</span>
              </div>
              <div className="cp-heading-xl mt-1 text-[15.5px] leading-snug text-[color:var(--text-primary)]">
                {item.title}
              </div>
              <div className="mt-1.5 line-clamp-2 text-[13px] leading-relaxed text-[color:var(--text-muted)]">
                {item.summary}
              </div>
            </div>
            <ExternalLink className="h-4 w-4 shrink-0 text-[color:var(--text-dim)]" />
          </a>
        </CardShell>
      ))}
    </div>
  );
}
