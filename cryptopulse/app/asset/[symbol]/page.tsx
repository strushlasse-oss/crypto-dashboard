import Link from "next/link";
import { ChevronLeft } from "lucide-react";
import { Sidebar, MobileNav } from "@/components/sidebar";
import { HeaderGauge } from "@/components/cards/header-gauge";
import { PriceCard } from "@/components/cards/price-card";
import { NewsCard } from "@/components/cards/news-card";
import { AIOverview } from "@/components/cards/ai-overview";
import { MarketMoodCard } from "@/components/cards/market-mood-card";
import { MarketPolicyCard } from "@/components/cards/market-policy-card";
import { FlowCard } from "@/components/cards/flow-card";
import { BearingCard } from "@/components/cards/bearing-card";
import { PulseCard } from "@/components/cards/pulse-card";
import { TickerCard } from "@/components/cards/ticker-card";
import { SessionsCard } from "@/components/cards/sessions-card";
import { RelativeStrengthCard } from "@/components/cards/relative-strength-card";
import { CmeGapsCard } from "@/components/cards/cme-gaps-card";
import { getMacroDesk } from "@/lib/macro-desk";

export const revalidate = 300;

type PageProps = {
  params: Promise<{ symbol: string }>;
};

export default async function AssetPage({ params }: PageProps) {
  const { symbol } = await params;
  const data = await getMacroDesk(symbol);

  return (
    <div className="relative flex min-h-screen">
      <Sidebar />
      <MobileNav />

      <main className="flex-1 px-5 pb-28 pt-6 md:ml-24 md:px-10 md:pb-12">
        {/* Back link */}
        <Link
          href="/asset/btc"
          className="inline-flex items-center gap-1 text-[12px] font-medium text-[color:var(--text-muted)] transition-colors hover:text-[color:var(--text-primary)]"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Back to AI Macro Desk
        </Link>

        {/* Header row: asset + gauges */}
        <div className="mt-5 flex flex-wrap items-center justify-between gap-5">
          <div className="flex items-center gap-5">
            <div
              className="flex h-14 w-14 items-center justify-center rounded-xl text-2xl font-black"
              style={{
                background: "linear-gradient(135deg, rgba(45,212,191,0.3), rgba(45,212,191,0.05))",
                color: "var(--accent-cp)",
                boxShadow: "inset 0 0 0 1px rgba(45,212,191,0.35)",
              }}
            >
              ₿
            </div>
            <div>
              <h1 className="cp-heading-xl text-[58px] leading-[0.95] uppercase">
                {data.asset.symbol}
              </h1>
              <div className="mt-1.5 text-[14px] font-medium text-[color:var(--text-muted)]">
                {data.asset.pair}
              </div>
            </div>
          </div>
          <div className="flex gap-3">
            {data.gauges.map((g) => (
              <HeaderGauge key={g.label} {...g} />
            ))}
          </div>
        </div>

        {/* Main grid */}
        <div className="mt-6 grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
          {/* LEFT column */}
          <div className="flex flex-col gap-5">
            <PriceCard
              symbol={data.asset.symbol}
              price={data.asset.price}
              deltaPct={data.asset.deltaPct}
              chart={data.asset.chart}
              delay={0.0}
            />
            <NewsCard items={data.news} delay={0.1} />
          </div>

          {/* RIGHT column */}
          <div className="flex flex-col gap-5">
            <AIOverview text={data.aiOverview} delay={0.05} />

            <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
              <MarketMoodCard data={data.mood} delay={0.1} />
              <MarketPolicyCard data={data.policy} delay={0.15} />
            </div>

            <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
              <FlowCard data={data.flow} delay={0.2} />
              <BearingCard data={data.bearing} delay={0.25} />
              <PulseCard data={data.pulse} delay={0.3} />
            </div>
          </div>
        </div>

        {/* CME Gaps (BTC only) */}
        {symbol === "btc" && data.cmeGaps && data.cmeGaps.length > 0 ? (
          <div className="mt-6">
            <CmeGapsCard gaps={data.cmeGaps} price={data.asset.price} delay={0.3} />
          </div>
        ) : null}

        {/* Ticker strip */}
        <div className="mt-6 grid grid-cols-2 gap-4 xl:grid-cols-4">
          {data.ticker.map((t, i) => (
            <TickerCard key={t.symbol} ticker={t} delay={0.35 + i * 0.04} />
          ))}
        </div>

        {/* Bottom row */}
        <div className="mt-6 grid grid-cols-1 gap-5 xl:grid-cols-[minmax(0,1fr)_minmax(0,2fr)]">
          <SessionsCard sessions={data.sessions} delay={0.5} />
          <RelativeStrengthCard rows={data.relativeStrength} delay={0.55} />
        </div>
      </main>
    </div>
  );
}
