import type { ReactNode } from "react";

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
