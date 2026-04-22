"use client";

import { useMemo, useState } from "react";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ArrowDownRight, ArrowUpRight } from "lucide-react";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { CardShell } from "./card-shell";
import { cn, formatPct, formatUsd } from "@/lib/utils";
import type { TrendPoint } from "@/lib/mock-data";

type Range = "1D" | "5D" | "1M";

type Props = {
  symbol: string;
  price: number;
  deltaPct: number;
  chart: TrendPoint[];
  delay?: number;
};

const RANGE_SLICE: Record<Range, number> = { "1D": 24, "5D": 40, "1M": 48 };

export function PriceCard({ symbol, price, deltaPct, chart, delay = 0 }: Props) {
  const [range, setRange] = useState<Range>("1D");
  const bullish = deltaPct >= 0;
  const lineColor = bullish ? "var(--bullish)" : "var(--bearish)";

  const data = useMemo(() => {
    const n = RANGE_SLICE[range];
    return chart.slice(-n);
  }, [chart, range]);

  return (
    <CardShell delay={delay}>
      <div className="flex items-start justify-between">
        <div>
          <div className="cp-label-caps">{symbol} / USD</div>
          <div className="mono mt-2 text-[40px] font-bold leading-none tabular">
            {formatUsd(price)}
          </div>
          <div
            className={cn(
              "cp-pill mt-3.5",
              bullish
                ? "bg-[color:var(--bullish)]/12 text-[color:var(--bullish)]"
                : "bg-[color:var(--bearish)]/12 text-[color:var(--bearish)]",
            )}
          >
            {bullish ? <ArrowUpRight className="h-3.5 w-3.5" /> : <ArrowDownRight className="h-3.5 w-3.5" />}
            {formatPct(deltaPct)}
          </div>
        </div>
        <Tabs value={range} onValueChange={(v) => setRange(v as Range)}>
          <TabsList className="h-9 bg-[color:var(--bg-elevated-2)] p-0.5">
            {(["1D", "5D", "1M"] as Range[]).map((r) => (
              <TabsTrigger
                key={r}
                value={r}
                className="h-8 px-3.5 text-[12px] font-bold tracking-wider data-[state=active]:bg-[color:var(--accent-glow)] data-[state=active]:text-[color:var(--accent-cp)]"
              >
                {r}
              </TabsTrigger>
            ))}
          </TabsList>
        </Tabs>
      </div>

      <div className="mt-5 h-[180px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
            <defs>
              <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={lineColor} stopOpacity={0.4} />
                <stop offset="100%" stopColor={lineColor} stopOpacity={0} />
              </linearGradient>
            </defs>
            <XAxis dataKey="t" hide />
            <YAxis
              domain={["dataMin", "dataMax"]}
              tickFormatter={(v) => `$${Math.round(v / 1000)}k`}
              width={40}
              tick={{ fill: "var(--text-dim)", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip
              cursor={{ stroke: "var(--border)" }}
              contentStyle={{
                background: "var(--bg-elevated-2)",
                border: "1px solid var(--border)",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelFormatter={() => ""}
              formatter={(v) => [formatUsd(Number(v)), "Price"]}
            />
            <Area
              type="monotone"
              dataKey="price"
              stroke={lineColor}
              strokeWidth={1.8}
              fill="url(#priceFill)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </CardShell>
  );
}
