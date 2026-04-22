import "server-only";

export type CmeGap = {
  low: number;
  high: number;
  sizePct: number;
  direction: "up" | "down";
  date: string;
  ageDays: number;
};

const YF = "https://query1.finance.yahoo.com/v8/finance/chart/BTC=F?interval=1d&range=2y";

type YahooChart = {
  chart: {
    result?: [
      {
        timestamp: number[];
        indicators: {
          quote: [{ open: (number | null)[]; high: (number | null)[]; low: (number | null)[]; close: (number | null)[] }];
        };
      },
    ];
  };
};

export async function getOpenGaps(): Promise<CmeGap[]> {
  try {
    const res = await fetch(YF, {
      headers: { "User-Agent": "Mozilla/5.0 CryptoPulse" },
      next: { revalidate: 3600 },
    });
    if (!res.ok) return [];
    const json = (await res.json()) as YahooChart;
    const r = json.chart.result?.[0];
    if (!r) return [];
    const ts = r.timestamp;
    const { open, high, low, close } = r.indicators.quote[0];

    const gaps: CmeGap[] = [];
    const now = Date.now();

    for (let i = 1; i < ts.length; i++) {
      const prevCloseRaw = close[i - 1];
      const currOpenRaw  = open[i];
      if (prevCloseRaw == null || currOpenRaw == null) continue;

      const prevDate = new Date(ts[i - 1] * 1000);
      if (prevDate.getUTCDay() !== 5) continue; // Friday

      const prevClose = prevCloseRaw;
      const currOpen = currOpenRaw;
      const sizePct = ((currOpen - prevClose) / prevClose) * 100;
      if (Math.abs(sizePct) < 0.3) continue;

      const direction: "up" | "down" = currOpen > prevClose ? "up" : "down";
      const gapLow  = Math.min(prevClose, currOpen);
      const gapHigh = Math.max(prevClose, currOpen);

      let filled = false;
      for (let j = i + 1; j < ts.length; j++) {
        const jl = low[j];
        const jh = high[j];
        if (jl == null || jh == null) continue;
        if (direction === "up" && jl <= gapLow) { filled = true; break; }
        if (direction === "down" && jh >= gapHigh) { filled = true; break; }
      }
      if (filled) continue;

      const gapDate = new Date(ts[i] * 1000);
      const ageDays = Math.floor((now - gapDate.getTime()) / 86_400_000);
      gaps.push({
        low: gapLow,
        high: gapHigh,
        sizePct,
        direction,
        date: gapDate.toISOString().slice(0, 10),
        ageDays,
      });
    }

    gaps.sort((a, b) => b.low - a.low);
    return gaps;
  } catch {
    return [];
  }
}
