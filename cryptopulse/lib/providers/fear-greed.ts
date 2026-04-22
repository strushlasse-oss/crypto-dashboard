import "server-only";

export type FearGreed = {
  value: number;
  classification: string;
  updated: number;
};

export async function getFearGreed(): Promise<FearGreed | null> {
  try {
    const res = await fetch("https://api.alternative.me/fng/?limit=1", {
      next: { revalidate: 900 },
    });
    if (!res.ok) return null;
    const json = (await res.json()) as {
      data: { value: string; value_classification: string; timestamp: string }[];
    };
    const row = json.data?.[0];
    if (!row) return null;
    return {
      value: Number(row.value),
      classification: row.value_classification,
      updated: Number(row.timestamp) * 1000,
    };
  } catch {
    return null;
  }
}
