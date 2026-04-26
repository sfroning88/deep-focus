import type { PropertyCard } from "@focus/types";
import { formatCurrency, toNum } from "@focus/utils";
import { SectionLabel } from "./KpiStrip";

type PrdDetailCardProps = {
  card: PropertyCard;
  snapshot: PropertyCard["snapshots"][number];
};

export function PrdDetailCard({ card, snapshot }: PrdDetailCardProps) {
  const occupancy = toNum(snapshot.occupancy) / 100;
  const occupiedUnits = card.totalUnits * occupancy;
  const days = occupiedUnits > 0 ? occupiedUnits * 365 : 1;

  const controllablePrd = toNum(snapshot.controllablePRD);
  const revenuePrd = toNum(snapshot.totalRevenues) / days;
  const expensePrd = toNum(snapshot.controllableExpenses) / days;

  return (
    <div className="border border-white/10 rounded-sm p-3 md:p-4">
      <SectionLabel>Controllable PRD Detail</SectionLabel>
      <div className="mt-2.5 md:mt-3 grid grid-cols-3 gap-2 md:gap-3">
        <PrdBox label="Controllable PRD" value={controllablePrd} />
        <PrdBox label="Revenue PRD" value={revenuePrd} />
        <PrdBox label="Expense PRD" value={expensePrd} highlight />
      </div>
    </div>
  );
}

function PrdBox({
  label,
  value,
  highlight,
}: {
  label: string;
  value: number;
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
      <p className="text-base md:text-xl font-semibold font-data-mono text-white">
        {formatCurrency(value)}
      </p>
      <p className="mt-0.5 text-[9px] md:text-[11px] text-white/40">{label}</p>
    </div>
  );
}
