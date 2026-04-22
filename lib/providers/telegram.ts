import "server-only";
import { TelegramClient } from "telegram";
import { StringSession } from "telegram/sessions/index.js";

export type TelegramMessage = {
  id: number;
  text: string;
  ageMinutes: number;
  link: string;
};

const CHANNEL = "WatcherGuru";

let cache: { items: TelegramMessage[]; ts: number } | null = null;
const CACHE_MS = 45_000;

export function isEnabled(): boolean {
  return !!(process.env.TG_API_ID && process.env.TG_API_HASH && process.env.TG_SESSION_STRING);
}

export async function getMessages(limit = 8): Promise<TelegramMessage[]> {
  if (cache && Date.now() - cache.ts < CACHE_MS) return cache.items;
  if (!isEnabled()) return [];

  const apiId   = Number(process.env.TG_API_ID);
  const apiHash = String(process.env.TG_API_HASH);
  const session = new StringSession(String(process.env.TG_SESSION_STRING));

  const client = new TelegramClient(session, apiId, apiHash, {
    connectionRetries: 1,
    useWSS: true,
  });

  try {
    await client.connect();
    const raw = await client.getMessages(CHANNEL, { limit });
    const now = Date.now();
    const items: TelegramMessage[] = [];
    for (const m of raw) {
      const text = (m.message ?? "").trim().replace(/\*\*/g, "").replace(/__/g, "");
      if (!text) continue;
      const sentAt = (m.date ?? 0) * 1000;
      const ageMinutes = Math.max(0, Math.floor((now - sentAt) / 60_000));
      items.push({
        id: m.id,
        text,
        ageMinutes,
        link: `https://t.me/${CHANNEL}/${m.id}`,
      });
    }
    cache = { items, ts: Date.now() };
    return items;
  } catch {
    return [];
  } finally {
    try { await client.disconnect(); } catch { /* ignore */ }
  }
}
