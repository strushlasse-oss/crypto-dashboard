import "server-only";

const FAPI  = "https://fapi.binance.com/fapi/v1";
const FDATA = "https://fapi.binance.com/futures/data";

const SYMBOL_MAP: Record<string, string> = {
  bitcoin:  "BTCUSDT",
  ethereum: "ETHUSDT",
  solana:   "SOLUSDT",
  ripple:   "XRPUSDT",
  dogecoin: "DOGEUSDT",
  cardano:  "ADAUSDT",
  binancecoin: "BNBUSDT",
};

export type LiqRow = {
  coinId: string;
  symbol: string;
  longPct: number;
  shortPct: number;
  lsRatio: number;
  oiChangePct: number | null;
  priceChangePct: number;
  pressure: "longs" | "shorts" | "neutral";
};

async function getJson<T>(url: string): Promise<T | null> {
  try {
    const res = await fetch(url, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function getLiquidationData(coinId: string): Promise<LiqRow | null> {
  const symbol = SYMBOL_MAP[coinId];
  if (!symbol) return null;

  const [ls, oi, ticker] = await Promise.all([
    getJson<{ longShortRatio: string; longAccount: string; shortAccount: string }[]>(
      `${FDATA}/globalLongShortAccountRatio?symbol=${symbol}&period=1h&limit=2`,
    ),
    getJson<{ sumOpenInterest: string }[]>(
      `${FDATA}/openInterestHist?symbol=${symbol}&period=1h&limit=2`,
    ),
    getJson<{ priceChangePercent: string }>(
      `${FAPI}/ticker/24hr?symbol=${symbol}`,
    ),
  ]);

  if (!ls || ls.length === 0 || !ticker) return null;

  const last = ls[ls.length - 1];
  const lsRatio  = Number(last.longShortRatio);
  const longPct  = Number(last.longAccount) * 100;
  const shortPct = Number(last.shortAccount) * 100;
  let oiChangePct: number | null = null;
  if (oi && oi.length >= 2) {
    const now  = Number(oi[oi.length - 1].sumOpenInterest);
    const prev = Number(oi[0].sumOpenInterest);
    if (prev > 0) oiChangePct = ((now - prev) / prev) * 100;
  }
  const priceChangePct = Number(ticker.priceChangePercent ?? 0);

  let pressure: LiqRow["pressure"] = "neutral";
  if (priceChangePct < -1.5 && oiChangePct != null && oiChangePct < -0.5) pressure = "longs";
  else if (priceChangePct > 1.5 && oiChangePct != null && oiChangePct < -0.5) pressure = "shorts";

  return { coinId, symbol, longPct, shortPct, lsRatio, oiChangePct, priceChangePct, pressure };
}

export async function getLiquidationsForCoins(coinIds: string[]): Promise<LiqRow[]> {
  const rows = await Promise.all(coinIds.map(getLiquidationData));
  return rows.filter((r): r is LiqRow => r !== null);
}
