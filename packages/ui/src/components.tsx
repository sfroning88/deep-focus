import type { ReactNode } from "react";
import { formatCurrency } from "@focus/utils";

export function Dot({ className }: { className?: string }) {
  return (
    <span className={`select-none ${className ?? "text-white/25"}`}>·</span>
  );
}

export function Badge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-sm border border-white/15 px-1.5 md:px-2 py-0.5 text-[10px] md:text-xs text-white/50 font-data-mono whitespace-nowrap">
      {children}
    </span>
  );
}

export function SectionLabel({ children }: { children: ReactNode }) {
  return (
    <h3 className="text-[10px] md:text-[11px] font-semibold uppercase tracking-[0.15em] text-white/40">
      {children}
    </h3>
  );
}

export function KpiCard({
  label,
  sublabel,
  accent,
  children,
}: {
  label: string;
  sublabel: string;
  accent?: boolean;
  children: ReactNode;
}) {
  return (
    <div
      className={`rounded-sm px-3 md:px-4 py-2.5 md:py-3 ${
        accent
          ? "bg-fhp-blue-800 text-white"
          : "border border-white/10 text-white"
      }`}
    >
      <p className="text-[10px] md:text-[11px] font-medium uppercase tracking-wider text-white/50">
        {label}
      </p>
      <p className="mt-0.5 md:mt-1 text-lg md:text-2xl font-semibold font-data-mono leading-tight">
        {children}
      </p>
      <p className="mt-0.5 text-[10px] md:text-xs text-white/40">{sublabel}</p>
    </div>
  );
}

export function ValueBox({
  label,
  value,
  highlight,
}: {
  label: string;
  value: number | null;
  highlight?: boolean;
}) {
  return (
    <div
      className={`rounded-sm px-2 md:px-4 py-2.5 md:py-3 text-center ${
        highlight
          ? "bg-fhp-blue-800/60 border border-fhp-blue-600/40"
          : "bg-white/[0.03] border border-white/10"
      }`}
    >
      {value === null ? (
        <p
          className="min-h-[1.5rem] md:min-h-8 flex items-center justify-center"
          aria-label="Not available"
        >
          <span className="block w-9 md:w-11 max-w-[60%] h-px bg-white/35 rounded-full" />
        </p>
      ) : (
        <p className="text-base md:text-xl font-semibold font-data-mono text-white">
          {formatCurrency(value)}
        </p>
      )}
      <p className="mt-0.5 text-[9px] md:text-[11px] text-white/40">{label}</p>
    </div>
  );
}

export function DeltaBox({
  delta,
  baseline,
}: {
  delta: number;
  baseline: number | null;
}) {
  const pct =
    baseline != null && baseline !== 0
      ? ((delta / Math.abs(baseline)) * 100).toFixed(1)
      : null;

  const isPositive = delta > 0;
  const isNeutral = delta === 0;

  const color = isNeutral
    ? "text-white/50"
    : isPositive
      ? "text-green-400"
      : "text-red-400";

  const sign = isPositive ? "+" : "";

  return (
    <div className="rounded-sm px-2 md:px-4 py-2.5 md:py-3 text-center bg-white/[0.03] border border-white/10">
      <p
        className={`text-base md:text-xl font-semibold font-data-mono ${color}`}
      >
        {sign}
        {formatCurrency(delta)}
      </p>
      {pct != null ? (
        <p className={`mt-0.5 text-[9px] md:text-[11px] ${color}`}>
          {sign}
          {pct}%
        </p>
      ) : (
        <p className="mt-0.5 text-[9px] md:text-[11px] text-white/40">
          Variance
        </p>
      )}
    </div>
  );
}
