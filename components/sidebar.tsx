"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Brain,
  CalendarDays,
  FileText,
  LayoutDashboard,
  TrendingUp,
  Users,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/utils";

type NavItem = {
  label: string;
  icon: LucideIcon;
  href: string;
  soon?: boolean;
};

const NAV: NavItem[] = [
  { label: "Dashboard",  icon: LayoutDashboard, href: "/dashboard" },
  { label: "Reports",    icon: FileText,        href: "/reports" },
  { label: "Calendar",   icon: CalendarDays,    href: "/calendar" },
  { label: "Macro Desk", icon: TrendingUp,      href: "/asset/btc" },
  { label: "Psychology", icon: Brain,           href: "#",         soon: true },
  { label: "Journal",    icon: BookOpen,        href: "#",         soon: true },
  { label: "Community",  icon: Users,           href: "#",         soon: true },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      className={cn(
        "z-20 flex shrink-0 flex-col items-center gap-1 border-r bg-[color:var(--bg-elevated)]/60 backdrop-blur-md",
        "fixed inset-y-0 left-0 hidden w-24 py-5 md:flex",
      )}
      style={{ borderColor: "var(--border-soft)" }}
    >
      <Link href="/asset/btc" className="mb-7 flex flex-col items-center gap-1.5">
        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[linear-gradient(135deg,rgba(45,212,191,0.3),rgba(45,212,191,0.05))] text-xl font-black text-[color:var(--accent-cp)] shadow-[inset_0_0_0_1px_rgba(45,212,191,0.3)]">
          ₿
        </div>
        <span className="cp-heading-xl text-[11px] uppercase tracking-[0.18em] text-[color:var(--accent-cp)]">
          Pulse
        </span>
      </Link>

      <nav className="flex w-full flex-col items-stretch gap-1 px-2">
        {NAV.map((item) => {
          const Icon = item.icon;
          const active =
            pathname === item.href ||
            (item.href.startsWith("/asset") && pathname?.startsWith("/asset"));
          return (
            <Link
              key={item.label}
              href={item.href}
              className={cn(
                "group relative flex flex-col items-center gap-1 rounded-xl px-1.5 py-2.5 transition-colors",
                active ? "bg-[color:var(--accent-glow)]" : "hover:bg-white/5",
              )}
            >
              {active && (
                <span className="absolute left-0 top-1/2 h-6 w-[3px] -translate-y-1/2 rounded-r-full bg-[color:var(--accent-cp)]" />
              )}
              <Icon
                className={cn(
                  "h-[22px] w-[22px] transition-colors",
                  active
                    ? "text-[color:var(--accent-cp)]"
                    : "text-[color:var(--text-muted)] group-hover:text-[color:var(--text-primary)]",
                )}
                strokeWidth={1.75}
              />
              <span
                className={cn(
                  "cp-heading-xl text-[10.5px] uppercase tracking-[0.12em] transition-colors",
                  active
                    ? "text-[color:var(--accent-cp)]"
                    : "text-[color:var(--text-muted)] group-hover:text-[color:var(--text-primary)]",
                )}
              >
                {item.label}
              </span>
              {item.soon && (
                <span className="cp-pill mt-0.5 border border-[color:var(--accent-cp)]/30 bg-[color:var(--accent-cp)]/10 text-[8px] tracking-wider text-[color:var(--accent-cp)]">
                  Soon
                </span>
              )}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

export function MobileNav() {
  const pathname = usePathname();
  return (
    <nav
      className="fixed inset-x-0 bottom-0 z-30 flex items-stretch justify-around border-t bg-[color:var(--bg-elevated)]/95 py-2 backdrop-blur-md md:hidden"
      style={{ borderColor: "var(--border-soft)" }}
    >
      {NAV.filter((n) => !n.soon).map((item) => {
        const Icon = item.icon;
        const active =
          pathname === item.href ||
          (item.href.startsWith("/asset") && pathname?.startsWith("/asset"));
        return (
          <Link
            key={item.label}
            href={item.href}
            className="flex flex-col items-center gap-0.5 px-2"
          >
            <Icon
              className={cn(
                "h-5 w-5",
                active
                  ? "text-[color:var(--accent-cp)]"
                  : "text-[color:var(--text-muted)]",
              )}
              strokeWidth={1.75}
            />
            <span
              className={cn(
                "text-[9px] uppercase tracking-wider",
                active
                  ? "text-[color:var(--accent-cp)]"
                  : "text-[color:var(--text-muted)]",
              )}
            >
              {item.label}
            </span>
          </Link>
        );
      })}
    </nav>
  );
}
