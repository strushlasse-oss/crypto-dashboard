import "server-only";

export type CryptoPanicItem = {
  title: string;
  url: string;
  source: string;
  domain: string;
  publishedAt: number;
  currencies: string[];
};

type CPRow = {
  title: string;
  url: string;
  published_at: string;
  source?: { title?: string; domain?: string };
  currencies?: { code: string }[];
};

export function isEnabled(): boolean {
  return !!process.env.CRYPTOPANIC_TOKEN;
}

export async function getNews(currencies?: string[], limit = 8): Promise<CryptoPanicItem[]> {
  const token = process.env.CRYPTOPANIC_TOKEN;
  if (!token) return [];
  const params = new URLSearchParams({ auth_token: token, public: "true" });
  if (currencies?.length) params.set("currencies", currencies.join(","));
  try {
    const res = await fetch(`https://cryptopanic.com/api/v1/posts/?${params}`, {
      next: { revalidate: 300 },
    });
    if (!res.ok) return [];
    const json = (await res.json()) as { results?: CPRow[] };
    const rows = (json.results ?? []).slice(0, limit);
    return rows.map((r) => ({
      title: r.title,
      url: r.url,
      source: r.source?.title ?? "CryptoPanic",
      domain: r.source?.domain ?? "cryptopanic.com",
      publishedAt: new Date(r.published_at).getTime(),
      currencies: (r.currencies ?? []).map((c) => c.code),
    }));
  } catch {
    return [];
  }
}
