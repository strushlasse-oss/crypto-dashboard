"use client";

import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";
import { CardShell } from "./card-shell";
import type { TickerEntry } from "@/lib/mock-data";
import { cn, formatPct, formatUsd } from "@/lib/utils";

type Props = { ticker: TickerEntry; delay?: number };

export function TickerCard({ ticker, delay = 0 }: Props) {
  const bullish = ticker.deltaPct >= 0;
  const color = bullish ? "var(--bullish)" : "var(--bearish)";
  const chart = ticker.spark.map((v, i) => ({ i, v }));
  const id = `spark-${ticker.symbol}`;

  return (
    <CardShell delay={delay} className="!p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="cp-heading-xl text-[15px] uppercase tracking-wide text-[color:var(--text-primary)]">
            {ticker.symbol}
          </div>
          <div className="text-[11px] font-medium text-[color:var(--text-muted)]">{ticker.pair}</div>
        </div>
        <div className="text-right">
          <div className="mono text-[16px] font-bold tabular">
            {formatUsd(ticker.price, { decimals: ticker.price > 100 ? 2 : 3 })}
          </div>
          <div
            className={cn(
              "mono mt-1 flex items-center justify-end gap-0.5 text-[12px] font-bold tabular",
            )}
            style={{ color }}
          >
            {bullish ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
            {formatPct(ticker.deltaPct)}
          </div>
        </div>
      </div>

      <div className="mt-3 h-14 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chart} margin={{ top: 2, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id={id} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.4} />
                <stop offset="100%" stopColor={color} stopOpacity={0} />
              </linearGradient>
            </defs>
            <Area
              type="monotone"
              dataKey="v"
              stroke={color}
              strokeWidth={1.5}
              fill={`url(#${id})`}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </CardShell>
  );
}
