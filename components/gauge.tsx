"use client";

import { motion } from "framer-motion";
import { useMemo } from "react";

export type GaugeSegment = {
  color: string;
  range: [number, number]; // in 0-100 units
};

export type GaugeProps = {
  value: number; // 0-100
  segments?: GaugeSegment[];
  label?: string;
  size?: number;
  thickness?: number;
};

const DEFAULT_SEGMENTS: GaugeSegment[] = [
  { color: "var(--bearish)", range: [0, 33] },
  { color: "var(--neutral)", range: [33, 66] },
  { color: "var(--bullish)", range: [66, 100] },
];

export function Gauge({
  value,
  segments = DEFAULT_SEGMENTS,
  label,
  size = 120,
  thickness = 8,
}: GaugeProps) {
  const clamped = Math.max(0, Math.min(100, value));
  const width = size;
  const height = size / 2 + thickness;
  const cx = width / 2;
  const cy = size / 2;
  const r = size / 2 - thickness / 2;

  const arcPath = useMemo(() => {
    const start = polar(cx, cy, r, 180);
    const end = polar(cx, cy, r, 0);
    return `M ${start.x} ${start.y} A ${r} ${r} 0 0 1 ${end.x} ${end.y}`;
  }, [cx, cy, r]);

  const segmentPaths = useMemo(
    () =>
      segments.map((s) => {
        const a1 = 180 - (s.range[0] / 100) * 180;
        const a2 = 180 - (s.range[1] / 100) * 180;
        const p1 = polar(cx, cy, r, a1);
        const p2 = polar(cx, cy, r, a2);
        const large = Math.abs(a1 - a2) > 180 ? 1 : 0;
        return {
          d: `M ${p1.x} ${p1.y} A ${r} ${r} 0 ${large} 1 ${p2.x} ${p2.y}`,
          color: s.color,
        };
      }),
    [segments, cx, cy, r],
  );

  const needleAngle = 180 - (clamped / 100) * 180;
  const needleEnd = polar(cx, cy, r - thickness / 2, needleAngle);
  const activeColor = segments.find(
    (s) => clamped >= s.range[0] && clamped <= s.range[1],
  )?.color ?? "var(--accent-cp)";

  return (
    <div className="flex flex-col items-center" style={{ width }}>
      <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        <defs>
          <filter id={`glow-${size}`} x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="2" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        {/* Track */}
        <path
          d={arcPath}
          stroke="var(--border)"
          strokeWidth={thickness}
          strokeLinecap="round"
          fill="none"
        />

        {/* Segments */}
        {segmentPaths.map((s, i) => (
          <path
            key={i}
            d={s.d}
            stroke={s.color}
            strokeWidth={thickness}
            strokeLinecap="butt"
            fill="none"
            opacity={0.55}
          />
        ))}

        {/* Needle */}
        <motion.line
          x1={cx}
          y1={cy}
          x2={needleEnd.x}
          y2={needleEnd.y}
          stroke={activeColor}
          strokeWidth={2.5}
          strokeLinecap="round"
          filter={`url(#glow-${size})`}
          initial={{ x2: polar(cx, cy, r - thickness / 2, 180).x, y2: polar(cx, cy, r - thickness / 2, 180).y }}
          animate={{ x2: needleEnd.x, y2: needleEnd.y }}
          transition={{ type: "spring", stiffness: 160, damping: 18 }}
        />
        <circle cx={cx} cy={cy} r={4} fill={activeColor} filter={`url(#glow-${size})`} />
      </svg>
      {label ? (
        <div className="cp-label-caps mt-1 text-center">{label}</div>
      ) : null}
    </div>
  );
}

function polar(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = (angleDeg * Math.PI) / 180;
  return {
    x: cx + r * Math.cos(rad),
    y: cy - r * Math.sin(rad),
  };
}
