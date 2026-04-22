import "server-only";

export function sma(values: number[], period: number): (number | null)[] {
  const out: (number | null)[] = [];
  let sum = 0;
  for (let i = 0; i < values.length; i++) {
    sum += values[i];
    if (i >= period) sum -= values[i - period];
    out.push(i >= period - 1 ? sum / period : null);
  }
  return out;
}

export function ema(values: number[], period: number): (number | null)[] {
  const k = 2 / (period + 1);
  const out: (number | null)[] = [];
  let prev: number | null = null;
  for (let i = 0; i < values.length; i++) {
    if (i < period - 1) {
      out.push(null);
      continue;
    }
    if (prev === null) {
      let s = 0;
      for (let j = i - period + 1; j <= i; j++) s += values[j];
      prev = s / period;
    } else {
      prev = values[i] * k + prev * (1 - k);
    }
    out.push(prev);
  }
  return out;
}

export function rsi(values: number[], period = 14): (number | null)[] {
  const out: (number | null)[] = new Array(values.length).fill(null);
  if (values.length <= period) return out;
  let gain = 0;
  let loss = 0;
  for (let i = 1; i <= period; i++) {
    const d = values[i] - values[i - 1];
    if (d >= 0) gain += d;
    else loss -= d;
  }
  gain /= period;
  loss /= period;
  out[period] = loss === 0 ? 100 : 100 - 100 / (1 + gain / loss);
  for (let i = period + 1; i < values.length; i++) {
    const d = values[i] - values[i - 1];
    const g = d > 0 ? d : 0;
    const l = d < 0 ? -d : 0;
    gain = (gain * (period - 1) + g) / period;
    loss = (loss * (period - 1) + l) / period;
    out[i] = loss === 0 ? 100 : 100 - 100 / (1 + gain / loss);
  }
  return out;
}

export function stdDev(values: number[], period: number): (number | null)[] {
  const out: (number | null)[] = [];
  for (let i = 0; i < values.length; i++) {
    if (i < period - 1) { out.push(null); continue; }
    const slice = values.slice(i - period + 1, i + 1);
    const mean = slice.reduce((a, b) => a + b, 0) / period;
    const v = slice.reduce((a, b) => a + (b - mean) ** 2, 0) / period;
    out.push(Math.sqrt(v));
  }
  return out;
}

export type Snapshot = {
  close: number;
  ema20: number | null;
  sma50: number | null;
  sma200: number | null;
  rsi14: number | null;
  stdev20: number | null;
};

export function snapshot(closes: number[]): Snapshot {
  if (closes.length === 0) return { close: 0, ema20: null, sma50: null, sma200: null, rsi14: null, stdev20: null };
  const e20 = ema(closes, 20);
  const s50 = sma(closes, 50);
  const s200 = sma(closes, 200);
  const r14 = rsi(closes, 14);
  const sd20 = stdDev(closes, 20);
  const i = closes.length - 1;
  return {
    close: closes[i],
    ema20: e20[i],
    sma50: s50[i],
    sma200: s200[i],
    rsi14: r14[i],
    stdev20: sd20[i],
  };
}

export function trendLabel(s: Snapshot): "Uptrend" | "Downtrend" | "Sideways" | "Unknown" {
  if (!s.sma50 || !s.sma200) return "Unknown";
  if (s.close > s.sma50 && s.sma50 > s.sma200) return "Uptrend";
  if (s.close < s.sma50 && s.sma50 < s.sma200) return "Downtrend";
  return "Sideways";
}
