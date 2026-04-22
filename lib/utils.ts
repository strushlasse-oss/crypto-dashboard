import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatUsd(value: number, opts?: { compact?: boolean; decimals?: number }) {
  const decimals = opts?.decimals ?? (Math.abs(value) >= 1 ? 2 : 4);
  if (opts?.compact && Math.abs(value) >= 1_000_000) {
    const units = [
      { v: 1e12, s: "T" },
      { v: 1e9, s: "B" },
      { v: 1e6, s: "M" },
    ];
    for (const u of units) {
      if (Math.abs(value) >= u.v) {
        return `$${(value / u.v).toFixed(2)}${u.s}`;
      }
    }
  }
  return `$${value.toLocaleString("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })}`;
}

export function formatPct(value: number, decimals = 2) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}%`;
}

export function deltaColor(value: number) {
  return value >= 0 ? "var(--bullish)" : "var(--bearish)";
}
