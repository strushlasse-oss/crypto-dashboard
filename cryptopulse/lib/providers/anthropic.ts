import "server-only";
import Anthropic from "@anthropic-ai/sdk";

export type AIDeskNarrative = {
  aiOverview: string;
  mood: {
    stance: "RISK-ON" | "RISK-OFF" | "NEUTRAL";
    needle: number;
    headline: string;
    body: string;
    footnote: string;
  };
  policy: {
    stance: "DOVISH" | "HAWKISH" | "NEUTRAL";
    headline: string;
    body: string;
    footnote: string;
  };
};

export type AIDeskContext = {
  symbol: string;
  name: string;
  price: number;
  delta24hPct: number;
  delta7dPct: number;
  btcDominance: number | null;
  totalMarketCapT: number | null;
  fngValue: number | null;
  fngClass: string | null;
  trend: string;
  rsi: number | null;
  edgeScore: number;
  edgeHeadline: string;
};

const FALLBACK = (ctx: AIDeskContext): AIDeskNarrative => {
  const fngTone =
    ctx.fngValue == null ? "NEUTRAL" :
    ctx.fngValue >= 55 ? "RISK-ON" :
    ctx.fngValue <= 35 ? "RISK-OFF" : "NEUTRAL";
  return {
    aiOverview:
      `${ctx.name} bei Edge ${ctx.edgeScore}/100 (${ctx.edgeHeadline}). ` +
      `${ctx.delta24hPct >= 0 ? "+" : ""}${ctx.delta24hPct.toFixed(2)} % heute, Trend ${ctx.trend.toLowerCase()}.`,
    mood: {
      stance: fngTone as AIDeskNarrative["mood"]["stance"],
      needle:
        fngTone === "RISK-ON" ? 75 :
        fngTone === "RISK-OFF" ? 25 : 50,
      headline: "Investor Positioning",
      body:
        ctx.fngValue != null
          ? `Fear & Greed Index bei ${ctx.fngValue} (${ctx.fngClass ?? "n/a"}) — Marktteilnehmer agieren entsprechend.`
          : "Live-Sentimentdaten derzeit nicht verfügbar.",
      footnote: `${fngTone}: Marktteilnehmer positionieren ${fngTone === "RISK-ON" ? "offensiv" : fngTone === "RISK-OFF" ? "defensiv" : "abwartend"}.`,
    },
    policy: {
      stance: "NEUTRAL",
      headline: "Global Economic Outlook",
      body: "Makro-Narrativ nicht verfügbar ohne Claude-Schlüssel.",
      footnote: "Set ANTHROPIC_API_KEY to enable live macro narrative.",
    },
  };
};

export async function getAIDeskNarrative(ctx: AIDeskContext): Promise<AIDeskNarrative> {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return FALLBACK(ctx);

  const client = new Anthropic({ apiKey: key });

  const prompt = `Du bist ein präziser Krypto-Markt-Analyst. Aktuelle Daten:
- Asset: ${ctx.name} (${ctx.symbol})
- Preis: $${ctx.price.toLocaleString("en-US")} (${ctx.delta24hPct >= 0 ? "+" : ""}${ctx.delta24hPct.toFixed(2)}% 24h, ${ctx.delta7dPct >= 0 ? "+" : ""}${ctx.delta7dPct.toFixed(2)}% 7d)
- BTC Dominanz: ${ctx.btcDominance != null ? ctx.btcDominance.toFixed(1) + "%" : "n/a"}
- Total Market Cap: ${ctx.totalMarketCapT != null ? "$" + ctx.totalMarketCapT.toFixed(2) + "T" : "n/a"}
- Fear & Greed: ${ctx.fngValue ?? "n/a"} (${ctx.fngClass ?? "n/a"})
- Trend: ${ctx.trend}, RSI14: ${ctx.rsi != null ? ctx.rsi.toFixed(0) : "n/a"}
- Edge Factor: ${ctx.edgeScore}/100 (${ctx.edgeHeadline})

Antworte ausschließlich als JSON-Objekt mit exakt diesen Feldern, ohne Markdown, ohne Erklärungen drumherum:

{
  "aiOverview": "2-3 englische Sätze: was treibt gerade den Markt, gezielt für diesen Coin. Konkret, keine Floskeln.",
  "mood": {
    "stance": "RISK-ON" | "RISK-OFF" | "NEUTRAL",
    "needle": 0-100 (0=max risk-off, 100=max risk-on),
    "headline": "Investor Positioning",
    "body": "1-2 englische Sätze zur aktuellen Investor-Positionierung im Crypto-Markt.",
    "footnote": "Kurzer Satz was die Stance bedeutet."
  },
  "policy": {
    "stance": "DOVISH" | "HAWKISH" | "NEUTRAL",
    "headline": "Global Economic Outlook",
    "body": "1-2 englische Sätze: Zentralbank-Lage + Auswirkung auf Crypto.",
    "footnote": "Kurzer Satz was die Stance bedeutet."
  }
}`;

  try {
    const msg = await client.messages.create({
      model: "claude-haiku-4-5-20251001",
      max_tokens: 600,
      messages: [{ role: "user", content: prompt }],
    });
    const text = msg.content
      .filter((b) => b.type === "text")
      .map((b) => (b as { type: "text"; text: string }).text)
      .join("")
      .trim();
    const match = text.match(/\{[\s\S]*\}/);
    if (!match) return FALLBACK(ctx);
    const parsed = JSON.parse(match[0]) as AIDeskNarrative;
    if (!parsed.aiOverview || !parsed.mood || !parsed.policy) return FALLBACK(ctx);
    parsed.mood.needle = Math.max(0, Math.min(100, Number(parsed.mood.needle) || 50));
    return parsed;
  } catch {
    return FALLBACK(ctx);
  }
}
