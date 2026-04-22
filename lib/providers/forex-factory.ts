import "server-only";

export type CalendarEvent = {
  title: string;
  country: string;
  impact: "High" | "Medium" | "Low" | string;
  date: number; // epoch ms
  forecast: string;
  previous: string;
  actual: string;
  diffSec: number;
};

type FFRow = {
  title: string;
  country: string;
  date: string;
  impact: string;
  forecast?: string;
  previous?: string;
  actual?: string;
};

const URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json";

export async function getCalendar(impactFilter: "High" | "Medium" | "Low" | null = "High"): Promise<CalendarEvent[]> {
  try {
    const res = await fetch(URL, {
      headers: { "User-Agent": "Mozilla/5.0 CryptoPulse" },
      next: { revalidate: 1800 },
    });
    if (!res.ok) return [];
    const raw = (await res.json()) as FFRow[];
    const now = Date.now();
    const out: CalendarEvent[] = [];
    for (const e of raw) {
      if (impactFilter && e.impact !== impactFilter) continue;
      const ts = new Date(e.date).getTime();
      if (Number.isNaN(ts)) continue;
      out.push({
        title: e.title,
        country: e.country,
        impact: e.impact,
        date: ts,
        forecast: e.forecast || "–",
        previous: e.previous || "–",
        actual: e.actual || "",
        diffSec: (ts - now) / 1000,
      });
    }
    out.sort((a, b) => a.date - b.date);
    return out;
  } catch {
    return [];
  }
}
