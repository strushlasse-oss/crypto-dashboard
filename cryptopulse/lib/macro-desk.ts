import "server-only";
import { COIN_MAP, getMarkets, getMarketChart, getGlobal, type MarketRow } from "./providers/coingecko";
import { getFearGreed } from "./providers/fear-greed";
import { getOpenGaps, type CmeGap } from "./providers/cme-gaps";
import { getAIDeskNarrative, type AIDeskContext } from "./providers/anthropic";
import { snapshot, trendLabel } from "./analysis/indicators";
import { computeEdge } from "./analysis/edge-factor";
import type { MacroDeskData, BulletCard } from "./mock-data";
import { MACRO_DESK_BTC } from "./mock-data";

const TICKER_SLUGS = ["eth", "sol", "bnb", "xrp"];
const RS_SLUGS = ["btc", "eth", "sol", "xrp", "doge", "ada"];

function priceChart(points: { t: number; price: number }[], n: number) {
  return points.slice(-n);
}

function buildFlow(row: MarketRow | undefined): BulletCard {
  if (!row || !row.total_volume || !row.market_cap) return MACRO_DESK_BTC.flow;
  const turnover = row.total_volume / row.market_cap; // daily $ volume / market cap
  const position =
    turnover < 0.015 ? 18 :
    turnover < 0.05  ? 52 :
                       82;
  const tone: BulletCard["tone"] = position < 33 ? "neutral" : position < 66 ? "bullish" : "bearish";
  const title = position < 33 ? "THIN FLOW" : position < 66 ? "HEALTHY FLOW" : "CROWDED FLOW";
  const bullets =
    position < 33 ? [
      "Turnover deutlich unter Durchschnitt — dünnes Orderbuch.",
      "Fills können außerhalb der Quote laufen.",
      "Positions-Größe konservativ halten.",
    ] : position < 66 ? [
      "Volume im erwarteten Bereich.",
      "Fills sollten zu Quote ausgeführt werden.",
      "Flow erlaubt Standard-Positionierung.",
    ] : [
      "Hoher Turnover — überlaufene Bewegungen möglich.",
      "Rückschlag-Risiko erhöht.",
      "Eng gestaffelte Stops, kleinere Size.",
    ];
  return { title, tone, position, stops: MACRO_DESK_BTC.flow.stops, bullets };
}

function buildBearing(closes: number[]): MacroDeskData["bearing"] {
  const fallback = MACRO_DESK_BTC.bearing;
  if (closes.length < 50) return fallback;
  const s = snapshot(closes);
  const label = trendLabel(s);
  const tone: BulletCard["tone"] = label === "Uptrend" ? "bullish" : label === "Downtrend" ? "bearish" : "neutral";
  const position = label === "Uptrend" ? 75 : label === "Downtrend" ? 20 : 50;
  const title =
    label === "Uptrend"   ? (s.rsi14 != null && s.rsi14 < 50 ? "CHOPPY UP TREND" : "CLEAN UP TREND") :
    label === "Downtrend" ? "DOWNTREND" :
                            "SIDEWAYS";
  const bullets =
    label === "Uptrend" ? [
      "Preis über SMA50 & SMA200 — übergeordneter Aufwärtstrend intakt.",
      s.rsi14 != null && s.rsi14 > 70 ? "RSI überkauft — Pullback möglich." : "Momentum trägt den Trend.",
      "Long-Setups bevorzugen, gegen den Trend handeln nur mit Signal.",
    ] : label === "Downtrend" ? [
      "Preis unter SMA50 & SMA200 — Abwärtstrend dominiert.",
      "Rallies bleiben verkäuferisch geprägt.",
      "Short-Setups bevorzugen, Long nur antizyklisch mit klarer Einstiegsmarke.",
    ] : [
      "Kein klarer Trend — Preis handelt zwischen den MAs.",
      "Range-Extreme beachten, Breakout-Trigger abwarten.",
      "Positions-Größe reduzieren bis Richtung klar ist.",
    ];
  const spark = closes.slice(-40);
  return { title, tone, position, stops: fallback.stops, bullets, spark };
}

function buildPulse(closes: number[]): BulletCard {
  const fallback = MACRO_DESK_BTC.pulse;
  if (closes.length < 30) return fallback;
  const s = snapshot(closes);
  if (s.stdev20 == null || s.close <= 0) return fallback;
  const volPct = (s.stdev20 / s.close) * 100;
  const position = volPct < 1.5 ? 18 : volPct < 3 ? 50 : 85;
  const tone: BulletCard["tone"] = volPct < 1.5 ? "neutral" : volPct < 3 ? "bullish" : "bearish";
  const title = volPct < 1.5 ? "QUIET PULSE" : volPct < 3 ? "TRADABLE PULSE" : "WILD PULSE";
  const bullets =
    volPct < 1.5 ? [
      "σ und Range unter Normal — Preis coiled.",
      "Setups brauchen Volatility-Expansion als Trigger.",
      "Engere Stops sind tragfähig in diesem Regime.",
    ] : volPct < 3 ? [
      "Volatilität in tradable range.",
      "Standard-Positionsgrößen passen.",
      "Normale Stop-Distanzen.",
    ] : [
      "Hohe Volatilität — Whipsaw-Risiko.",
      "Size reduzieren, Stops weiter fassen.",
      "Nur bei klaren Signalen handeln.",
    ];
  return { title, tone, position, stops: fallback.stops, bullets };
}

function toneForPct(pct: number): "bullish" | "bearish" | "neutral" {
  if (pct > 0.5) return "bullish";
  if (pct < -0.5) return "bearish";
  return "neutral";
}

function buildSessions(): MacroDeskData["sessions"] {
  const h = new Date().getUTCHours();
  const inRange = (start: number, end: number) => h >= start && h < end;
  return [
    { name: "Asia",   timezone: "Tokyo",  active: inRange(0, 9),   rangeStart: 0,  rangeEnd: 9  },
    { name: "Europe", timezone: "London", active: inRange(7, 16),  rangeStart: 7,  rangeEnd: 16 },
    { name: "US",     timezone: "NY",     active: inRange(13, 22), rangeStart: 13, rangeEnd: 22 },
  ];
}

export async function getMacroDesk(slug: string): Promise<MacroDeskData> {
  const coin = COIN_MAP[slug] ?? COIN_MAP.btc;
  const slugs = Array.from(new Set([coin.symbol.toLowerCase(), ...TICKER_SLUGS, ...RS_SLUGS]));

  const [markets, chart, fng, global, gaps] = await Promise.all([
    getMarkets(slugs),
    getMarketChart(slug, 200),
    getFearGreed(),
    getGlobal(),
    slug === "btc" ? getOpenGaps() : Promise.resolve([] as CmeGap[]),
  ]);

  const byId = new Map(markets.map((m) => [m.id, m]));
  const assetRow = byId.get(coin.id);

  // Fallback to mock if we don't even have a price
  if (!assetRow) return { ...MACRO_DESK_BTC, asset: { ...MACRO_DESK_BTC.asset, symbol: coin.symbol } };

  const closes = chart.map((p) => p.price);
  const snap = snapshot(closes);
  const edge = computeEdge(snap, fng?.value ?? null);
  const trend = trendLabel(snap);

  // Gauges
  const bias =
    edge.label === "strong" ? { value: "Bullish", tone: "bullish" as const } :
    edge.label === "low"    ? { value: "Bearish", tone: "bearish" as const } :
                              { value: "Neutral", tone: "neutral" as const };

  const technicalNeedle =
    trend === "Uptrend"   ? 78 :
    trend === "Downtrend" ? 22 :
                            50;
  const technicalTone: "bullish" | "bearish" | "neutral" =
    trend === "Uptrend"   ? "bullish" :
    trend === "Downtrend" ? "bearish" :
                            "neutral";
  const technicalValue = trend === "Uptrend" ? "Buy" : trend === "Downtrend" ? "Sell" : "Hold";

  // AI narrative
  const aiCtx: AIDeskContext = {
    symbol: coin.symbol,
    name: coin.name,
    price: assetRow.current_price,
    delta24hPct: assetRow.price_change_percentage_24h_in_currency ?? 0,
    delta7dPct:  assetRow.price_change_percentage_7d_in_currency ?? 0,
    btcDominance: global?.btc_dominance ?? null,
    totalMarketCapT: global ? global.total_market_cap_usd / 1e12 : null,
    fngValue: fng?.value ?? null,
    fngClass: fng?.classification ?? null,
    trend,
    rsi: snap.rsi14,
    edgeScore: edge.score,
    edgeHeadline: edge.headline,
  };
  const narrative = await getAIDeskNarrative(aiCtx);

  // Ticker strip
  const ticker = TICKER_SLUGS.map((s) => {
    const row = byId.get(COIN_MAP[s].id);
    if (!row) {
      const fallback = MACRO_DESK_BTC.ticker.find((t) => t.symbol.startsWith(COIN_MAP[s].symbol));
      return fallback ?? MACRO_DESK_BTC.ticker[0];
    }
    return {
      symbol: `${COIN_MAP[s].symbol}USD`,
      pair: COIN_MAP[s].pair,
      price: row.current_price,
      deltaPct: row.price_change_percentage_24h_in_currency ?? 0,
      spark: row.sparkline_in_7d?.price?.slice(-40) ?? [],
    };
  });

  // Relative strength: 7d% vs mean
  const rsRows = RS_SLUGS.map((s) => {
    const row = byId.get(COIN_MAP[s].id);
    return { symbol: COIN_MAP[s].symbol, pct7d: row?.price_change_percentage_7d_in_currency ?? 0 };
  });
  const mean7d = rsRows.reduce((a, r) => a + r.pct7d, 0) / rsRows.length;
  const spread = Math.max(...rsRows.map((r) => Math.abs(r.pct7d - mean7d))) || 1;
  const relativeStrength = rsRows.map((r) => ({
    symbol: r.symbol,
    value: Number(((r.pct7d - mean7d) / spread).toFixed(2)),
  }));

  // Compose
  const data: MacroDeskData = {
    asset: {
      symbol: coin.symbol,
      name: coin.name,
      pair: coin.pair,
      price: assetRow.current_price,
      deltaPct: assetRow.price_change_percentage_24h_in_currency ?? 0,
      chart: priceChart(chart, 48),
    },
    gauges: [
      { label: "Bias", value: bias.value, needle: edge.score, tone: bias.tone },
      { label: "Technical", value: technicalValue, needle: technicalNeedle, tone: technicalTone },
      { label: "AI Confidence", value: `${edge.score}%`, needle: edge.score, tone: toneForPct(edge.score - 50) },
    ],
    aiOverview: narrative.aiOverview,
    news: MACRO_DESK_BTC.news, // news still mocked — see note below
    mood: {
      ageMinutes: fng ? Math.max(1, Math.floor((Date.now() - fng.updated) / 60_000)) : 5,
      stance: narrative.mood.stance,
      needle: narrative.mood.needle,
      headline: narrative.mood.headline,
      body: narrative.mood.body,
      footnote: narrative.mood.footnote,
    },
    policy: {
      ageMinutes: 15,
      stance: narrative.policy.stance,
      headline: narrative.policy.headline,
      body: narrative.policy.body,
      footnote: narrative.policy.footnote,
    },
    flow: buildFlow(assetRow),
    bearing: buildBearing(closes),
    pulse: buildPulse(closes),
    ticker,
    sessions: buildSessions(),
    relativeStrength,
    cmeGaps: gaps,
  };

  return data;
}
