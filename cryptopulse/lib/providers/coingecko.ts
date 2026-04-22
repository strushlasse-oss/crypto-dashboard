import "server-only";

const BASE = "https://api.coingecko.com/api/v3";

export const COIN_MAP: Record<string, { id: string; name: string; symbol: string; pair: string }> = {
  btc:  { id: "bitcoin",      name: "Bitcoin",   symbol: "BTC",  pair: "Bitcoin / US Dollar" },
  eth:  { id: "ethereum",     name: "Ethereum",  symbol: "ETH",  pair: "Ethereum / US Dollar" },
  sol:  { id: "solana",       name: "Solana",    symbol: "SOL",  pair: "Solana / US Dollar" },
  bnb:  { id: "binancecoin",  name: "BNB",       symbol: "BNB",  pair: "BNB / US Dollar" },
  xrp:  { id: "ripple",       name: "XRP",       symbol: "XRP",  pair: "XRP / US Dollar" },
  doge: { id: "dogecoin",     name: "Dogecoin",  symbol: "DOGE", pair: "Dogecoin / US Dollar" },
  ada:  { id: "cardano",      name: "Cardano",   symbol: "ADA",  pair: "Cardano / US Dollar" },
};

export type MarketRow = {
  id: string;
  symbol: string;
  name: string;
  image: string;
  current_price: number;
  market_cap: number;
  price_change_percentage_1h_in_currency?: number;
  price_change_percentage_24h_in_currency?: number;
  price_change_percentage_7d_in_currency?: number;
  price_change_percentage_30d_in_currency?: number;
  sparkline_in_7d?: { price: number[] };
  total_volume: number;
};

async function getJson<T>(url: string, revalidate: number): Promise<T | null> {
  try {
    const res = await fetch(url, { next: { revalidate } });
    if (!res.ok) return null;
    return (await res.json()) as T;
  } catch {
    return null;
  }
}

export async function getMarkets(slugs: string[]): Promise<MarketRow[]> {
  const ids = slugs.map((s) => COIN_MAP[s]?.id).filter(Boolean).join(",");
  if (!ids) return [];
  const url =
    `${BASE}/coins/markets?vs_currency=usd&ids=${ids}` +
    `&order=market_cap_desc&per_page=${slugs.length}&page=1` +
    `&sparkline=true&price_change_percentage=1h,24h,7d,30d`;
  return (await getJson<MarketRow[]>(url, 300)) ?? [];
}

export type ChartPoint = { t: number; price: number };

export async function getMarketChart(slug: string, days: number): Promise<ChartPoint[]> {
  const id = COIN_MAP[slug]?.id;
  if (!id) return [];
  const url = `${BASE}/coins/${id}/market_chart?vs_currency=usd&days=${days}`;
  const data = await getJson<{ prices: [number, number][] }>(url, 900);
  if (!data?.prices) return [];
  return data.prices.map(([t, price]) => ({ t, price }));
}

export type Global = {
  total_market_cap_usd: number;
  market_cap_change_24h: number;
  btc_dominance: number;
};

export async function getGlobal(): Promise<Global | null> {
  const data = await getJson<{
    data: {
      total_market_cap: { usd: number };
      market_cap_change_percentage_24h_usd: number;
      market_cap_percentage: { btc: number };
    };
  }>(`${BASE}/global`, 600);
  if (!data?.data) return null;
  return {
    total_market_cap_usd: data.data.total_market_cap.usd,
    market_cap_change_24h: data.data.market_cap_change_percentage_24h_usd,
    btc_dominance: data.data.market_cap_percentage.btc,
  };
}
