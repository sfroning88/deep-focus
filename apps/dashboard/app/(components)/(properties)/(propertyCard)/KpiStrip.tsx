import type { PropertyCard } from "@focus/types";
import { formatCompactCurrency, formatDate, formatPercent } from "@focus/utils";

type KpiStripProps = {
  card: PropertyCard;
  latestSnapshot: PropertyCard["snapshots"][number];
};

export function KpiStrip({ card, latestSnapshot }: KpiStripProps) {
  const occupancy = latestSnapshot.occupancy;
  const reportedLabel = formatDate(latestSnapshot.reportedAt);

  return (
    <div>
      <SectionLabel>
        Key Metrics — Latest Snapshot ({reportedLabel})
      </SectionLabel>
      <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-2 md:gap-3">
        <KpiCard
          label="Occupancy"
          sublabel={`of ${card.totalUnits} units`}
          accent
        >
          {formatPercent(occupancy)}
        </KpiCard>
        <KpiCard label="Total revenues" sublabel="trailing period">
          {formatCompactCurrency(latestSnapshot.totalRevenues)}
        </KpiCard>
        <KpiCard label="Operating margin" sublabel="controllable basis">
          {formatPercent(latestSnapshot.operatingMargin)}
        </KpiCard>
        <KpiCard label="Controllable PRD" sublabel="per res. per day">
          {formatCompactCurrency(latestSnapshot.controllablePRD)}
        </KpiCard>
      </div>
    </div>
  );
}

function KpiCard({
  label,
  sublabel,
  accent,
  children,
}: {
  label: string;
  sublabel: string;
  accent?: boolean;
  children: React.ReactNode;
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

export function SectionLabel({ children }: { children: React.ReactNode }) {
  return (
    <h3 className="text-[10px] md:text-[11px] font-semibold uppercase tracking-[0.15em] text-white/40">
      {children}
    </h3>
  );
}
