import "server-only";
import type { Snapshot } from "./indicators";

export type EdgeResult = {
  score: number;
  label: "strong" | "mixed" | "low";
  headline: string;
  comment: string;
  components: { name: string; points: number; maxPoints: number; note: string }[];
};

export function computeEdge(snap: Snapshot, fng: number | null): EdgeResult {
  const components: EdgeResult["components"] = [];

  // Trend (40) — SMA stack
  let trendPts = 0;
  let trendNote = "Trend-Daten unvollständig";
  if (snap.sma50 && snap.sma200) {
    if (snap.close > snap.sma50 && snap.sma50 > snap.sma200) {
      trendPts = 40;
      trendNote = "Preis > SMA50 > SMA200 (Uptrend)";
    } else if (snap.close < snap.sma50 && snap.sma50 < snap.sma200) {
      trendPts = 5;
      trendNote = "Preis < SMA50 < SMA200 (Downtrend)";
    } else {
      trendPts = 20;
      trendNote = "Gemischte MA-Struktur";
    }
  }
  components.push({ name: "Trend", points: trendPts, maxPoints: 40, note: trendNote });

  // Momentum (25) — RSI
  let rsiPts = 12;
  let rsiNote = "RSI neutral";
  if (snap.rsi14 != null) {
    if (snap.rsi14 >= 55 && snap.rsi14 <= 70) {
      rsiPts = 25;
      rsiNote = `RSI ${snap.rsi14.toFixed(0)} (bullish momentum)`;
    } else if (snap.rsi14 >= 45 && snap.rsi14 < 55) {
      rsiPts = 17;
      rsiNote = `RSI ${snap.rsi14.toFixed(0)} (sweet-spot)`;
    } else if (snap.rsi14 > 70) {
      rsiPts = 10;
      rsiNote = `RSI ${snap.rsi14.toFixed(0)} (überkauft)`;
    } else if (snap.rsi14 < 30) {
      rsiPts = 8;
      rsiNote = `RSI ${snap.rsi14.toFixed(0)} (überverkauft)`;
    } else {
      rsiPts = 12;
      rsiNote = `RSI ${snap.rsi14.toFixed(0)}`;
    }
  }
  components.push({ name: "Momentum", points: rsiPts, maxPoints: 25, note: rsiNote });

  // Volatility (20) — lower volatility → higher score (cleaner setups)
  let volPts = 10;
  let volNote = "Volatilität n/a";
  if (snap.stdev20 != null && snap.close > 0) {
    const volPct = (snap.stdev20 / snap.close) * 100;
    if (volPct < 1.5) { volPts = 20; volNote = `σ niedrig (${volPct.toFixed(2)} %)`; }
    else if (volPct < 3) { volPts = 14; volNote = `σ moderat (${volPct.toFixed(2)} %)`; }
    else { volPts = 6; volNote = `σ hoch (${volPct.toFixed(2)} %)`; }
  }
  components.push({ name: "Volatilität", points: volPts, maxPoints: 20, note: volNote });

  // Sentiment (15) — Fear & Greed
  let fngPts = 7;
  let fngNote = "Sentiment n/a";
  if (fng != null) {
    if (fng >= 55 && fng <= 75) { fngPts = 15; fngNote = `F&G ${fng} (Greed – Rückenwind)`; }
    else if (fng > 75)          { fngPts = 8;  fngNote = `F&G ${fng} (Extreme Greed)`; }
    else if (fng >= 40)         { fngPts = 10; fngNote = `F&G ${fng} (neutral)`; }
    else if (fng >= 25)         { fngPts = 6;  fngNote = `F&G ${fng} (Fear)`; }
    else                        { fngPts = 12; fngNote = `F&G ${fng} (Extreme Fear – contrarian)`; }
  }
  components.push({ name: "Sentiment", points: fngPts, maxPoints: 15, note: fngNote });

  const score = Math.round(components.reduce((a, c) => a + c.points, 0));
  let label: EdgeResult["label"] = "mixed";
  if (score >= 70) label = "strong";
  else if (score < 45) label = "low";

  const headline =
    label === "strong" ? "Strong Setup" :
    label === "low"    ? "Weak Setup"   :
    "Mixed Setup";

  const comment =
    label === "strong"
      ? "Trend, Momentum und Sentiment ziehen gemeinsam nach oben — saubere Setup-Bedingungen."
      : label === "low"
      ? "Mehrere Komponenten schwach — defensive Positionierung oder abwarten."
      : "Gemischtes Bild: einzelne Komponenten stark, andere schwach — selektiv traden.";

  return { score, label, headline, comment, components };
}
