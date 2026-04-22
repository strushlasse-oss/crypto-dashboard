"use client";

import { motion } from "framer-motion";

export type GradientStop = { label: string; color: string };

export type GradientBarProps = {
  stops: GradientStop[];
  position: number; // 0-100
};

export function GradientBar({ stops, position }: GradientBarProps) {
  const clamped = Math.max(0, Math.min(100, position));
  const gradient = `linear-gradient(90deg, ${stops
    .map((s, i) => `${s.color} ${(i / (stops.length - 1)) * 100}%`)
    .join(", ")})`;

  return (
    <div className="w-full">
      <div className="relative h-2 w-full rounded-full" style={{ background: gradient, opacity: 0.85 }}>
        <motion.div
          initial={{ left: 0 }}
          animate={{ left: `${clamped}%` }}
          transition={{ type: "spring", stiffness: 180, damping: 20 }}
          className="absolute -top-1.5 -translate-x-1/2"
        >
          <div className="flex flex-col items-center">
            <div className="h-1.5 w-1.5 rounded-full bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)]" />
            <div className="mt-0.5 h-4 w-0.5 rounded-full bg-white" />
          </div>
        </motion.div>
      </div>
      <div className="mt-2 flex justify-between">
        {stops.map((s) => (
          <span
            key={s.label}
            className="text-[10px] font-medium uppercase tracking-wider"
            style={{ color: s.color }}
          >
            {s.label}
          </span>
        ))}
      </div>
    </div>
  );
}
