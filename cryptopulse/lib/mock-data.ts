export type TrendPoint = { t: number; price: number };

export type NewsItem = {
  source: string;
  domain: string;
  ageMinutes: number;
  title: string;
  summary: string;
  url: string;
};

export type GaugeData = {
  label: string;
  value: string;
  needle: number;
  tone: "bullish" | "bearish" | "neutral";
};

export type BulletCard = {
  title: string;
  tone: "bullish" | "bearish" | "neutral";
  bullets: string[];
  position: number;
  stops: { label: string; color: string }[];
};

export type TickerEntry = {
  symbol: string;
  pair: string;
  price: number;
  deltaPct: number;
  spark: number[];
};

export type RelativeStrength = {
  symbol: string;
  value: number;
};

export type CmeGap = {
  low: number;
  high: number;
  sizePct: number;
  direction: "up" | "down";
  date: string;
  ageDays: number;
};

export type CalendarEventLite = {
  title: string;
  country: string;
  date: number;
  diffSec: number;
  forecast: string;
  previous: string;
  actual: string;
};

export type LiquidationLite = {
  coinId: string;
  symbol: string;
  longPct: number;
  shortPct: number;
  lsRatio: number;
  oiChangePct: number | null;
  pressure: "longs" | "shorts" | "neutral";
};

export type NewsLite = {
  title: string;
  url: string;
  source: string;
  domain: string;
  ageMinutes: number;
};

export type TelegramLite = {
  id: number;
  text: string;
  ageMinutes: number;
  link: string;
};

export type MacroDeskData = {
  asset: {
    symbol: string;
    name: string;
    pair: string;
    price: number;
    deltaPct: number;
    chart: TrendPoint[];
  };
  gauges: GaugeData[];
  aiOverview: string;
  news: NewsItem[];
  mood: {
    ageMinutes: number;
    stance: "RISK-ON" | "RISK-OFF" | "NEUTRAL";
    needle: number;
    headline: string;
    body: string;
    footnote: string;
  };
  policy: {
    ageMinutes: number;
    stance: "DOVISH" | "HAWKISH" | "NEUTRAL";
    headline: string;
    body: string;
    footnote: string;
  };
  flow: BulletCard;
  bearing: BulletCard & { spark: number[] };
  pulse: BulletCard;
  ticker: TickerEntry[];
  sessions: { name: string; timezone: string; active: boolean; rangeStart: number; rangeEnd: number }[];
  relativeStrength: RelativeStrength[];
  cmeGaps?: CmeGap[];
  calendar?: CalendarEventLite[];
  liquidations?: LiquidationLite[];
  telegram?: TelegramLite[];
  fng?: { value: number; classification: string } | null;
};

// Deterministic pseudo-random walk so SSR and client match.
function seededRandom(seed: number) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) % 4294967296;
    return s / 4294967296;
  };
}

export function generateWalk(start: number, n: number, drift: number, vol: number, seed = 42): number[] {
  const rand = seededRandom(seed);
  const out: number[] = [];
  let price = start;
  for (let i = 0; i < n; i++) {
    const shock = (rand() - 0.5) * 2 * vol;
    price = price * (1 + drift + shock);
    out.push(Number(price.toFixed(2)));
  }
  return out;
}

function buildChart(start: number, n: number, drift: number, vol: number, seed: number): TrendPoint[] {
  const walk = generateWalk(start, n, drift, vol, seed);
  const now = Date.UTC(2026, 3, 22, 12, 0, 0);
  const step = 60 * 60 * 1000; // hourly
  return walk.map((price, i) => ({ t: now - (walk.length - 1 - i) * step, price }));
}

export const MACRO_DESK_BTC: MacroDeskData = {
  asset: {
    symbol: "BTC",
    name: "Bitcoin",
    pair: "Bitcoin / US Dollar",
    price: 104_285.5,
    deltaPct: 1.84,
    chart: buildChart(102_400, 48, 0.0008, 0.006, 11),
  },
  gauges: [
    { label: "Bias", value: "Bullish", needle: 78, tone: "bullish" },
    { label: "Technical", value: "Buy", needle: 70, tone: "bullish" },
    { label: "AI Confidence", value: "72%", needle: 72, tone: "bullish" },
  ],
  aiOverview:
    "Spot ETF inflows hit a 3-week high at +$480M while long-term holders continue accumulation. Fed minutes signaling a dovish pivot is fueling risk-on positioning heading into the weekend.",
  news: [
    {
      source: "CoinDesk",
      domain: "coindesk.com",
      ageMinutes: 12,
      title: "Spot Bitcoin ETFs Log $480M Weekly Inflow as Price Pushes Toward New Range",
      summary:
        "Institutional appetite accelerates with BlackRock's IBIT capturing the majority of fresh allocations amid a softening dollar.",
      url: "https://www.coindesk.com/",
    },
    {
      source: "The Block",
      domain: "theblock.co",
      ageMinutes: 34,
      title: "Long-term Holders Add Another 58K BTC to Cold Storage in April",
      summary:
        "Glassnode data confirms continued distribution compression — supply held >155 days climbs back above 74 %.",
      url: "https://www.theblock.co/",
    },
    {
      source: "Cointelegraph",
      domain: "cointelegraph.com",
      ageMinutes: 58,
      title: "FOMC Minutes Hint at Cuts: Risk Assets Catch a Bid",
      summary:
        "Treasury yields slip as committee members acknowledge cooling labor prints; BTC and ETH lead the rotation.",
      url: "https://cointelegraph.com/",
    },
  ],
  mood: {
    ageMinutes: 33,
    stance: "RISK-ON",
    needle: 76,
    headline: "Investor Positioning",
    body: "Strong bid across majors as BTC ETF flows remain positive. Altcoins showing rotational strength.",
    footnote: "Risk-On: investors are adding to risk assets.",
  },
  policy: {
    ageMinutes: 41,
    stance: "DOVISH",
    headline: "Global Economic Outlook",
    body: "Central banks pivoting toward easing; labor markets are cooling without breaking. Crypto benefits from liquidity expansion.",
    footnote: "DOVISH: Central banks leaning toward easier policy.",
  },
  flow: {
    title: "HEALTHY FLOW",
    tone: "bullish",
    position: 52,
    stops: [
      { label: "Thin", color: "#F59E0B" },
      { label: "Healthy", color: "#22C55E" },
      { label: "Crowded", color: "#EF4444" },
    ],
    bullets: [
      "Volume within the expected range.",
      "Fills should execute at quoted prices.",
      "Flow conditions support standard position sizing.",
    ],
  },
  bearing: {
    title: "CHOPPY UP TREND",
    tone: "bullish",
    position: 60,
    stops: [
      { label: "Down", color: "#EF4444" },
      { label: "Choppy", color: "#F59E0B" },
      { label: "Up", color: "#22C55E" },
    ],
    bullets: [
      "General upward bias but RSI shows indecision.",
      "Setups are valid but stop-outs more frequent.",
      "Wait for a cleaner impulse before committing.",
    ],
    spark: generateWalk(60, 36, 0.002, 0.03, 17),
  },
  pulse: {
    title: "QUIET PULSE",
    tone: "neutral",
    position: 18,
    stops: [
      { label: "Quiet", color: "#3B82F6" },
      { label: "Tradable", color: "#22C55E" },
      { label: "Wild", color: "#EF4444" },
    ],
    bullets: [
      "ATR and BB width below normal — price is coiling.",
      "Setups need a volatility-expansion trigger before entry.",
      "Stops tighter than usual are viable in this environment.",
    ],
  },
  ticker: [
    {
      symbol: "ETHUSD",
      pair: "Ethereum / USD",
      price: 3_892.4,
      deltaPct: 2.15,
      spark: generateWalk(3800, 40, 0.0012, 0.01, 31),
    },
    {
      symbol: "SOLUSD",
      pair: "Solana / USD",
      price: 218.65,
      deltaPct: -0.88,
      spark: generateWalk(225, 40, -0.0004, 0.012, 32),
    },
    {
      symbol: "BNBUSD",
      pair: "BNB / USD",
      price: 712.3,
      deltaPct: -0.42,
      spark: generateWalk(720, 40, -0.0002, 0.008, 33),
    },
    {
      symbol: "XRPUSD",
      pair: "XRP / USD",
      price: 2.847,
      deltaPct: 4.12,
      spark: generateWalk(2.65, 40, 0.002, 0.015, 34),
    },
  ],
  sessions: [
    { name: "Asia",   timezone: "Tokyo",  active: false, rangeStart: 0,  rangeEnd: 9  },
    { name: "Europe", timezone: "London", active: true,  rangeStart: 7,  rangeEnd: 16 },
    { name: "US",     timezone: "NY",     active: false, rangeStart: 13, rangeEnd: 22 },
  ],
  relativeStrength: [
    { symbol: "BTC",  value:  0.72 },
    { symbol: "ETH",  value:  0.41 },
    { symbol: "SOL",  value:  0.18 },
    { symbol: "XRP",  value:  0.56 },
    { symbol: "DOGE", value: -0.22 },
    { symbol: "ADA",  value: -0.48 },
  ],
};

export function getMacroDesk(symbol: string): MacroDeskData {
  void symbol;
  return MACRO_DESK_BTC;
}
