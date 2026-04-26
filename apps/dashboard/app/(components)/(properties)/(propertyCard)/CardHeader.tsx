import { X } from "lucide-react";
import type { PropertyCard } from "@focus/types";

type CardHeaderProps = {
  card: PropertyCard;
  onClose: () => void;
};

export function CardHeader({ card, onClose }: CardHeaderProps) {
  return (
    <div className="flex items-start justify-between gap-3">
      <div className="min-w-0">
        <h2 className="text-base md:text-xl font-semibold text-white truncate">
          {card.name}
        </h2>
        <div className="mt-1 flex flex-wrap items-center gap-x-1.5 md:gap-x-2 gap-y-1 text-xs md:text-sm text-white/60">
          <span className="break-words">
            {card.address}, {card.city}, {card.state} {card.zip}
          </span>
          <Dot />
          <span>{card.msa.name}</span>
          <Dot />
          <Badge>Built {card.yearBuilt}</Badge>
          <Badge>{card.totalUnits} units</Badge>
        </div>
      </div>
      <button
        type="button"
        onClick={onClose}
        className="shrink-0 p-1.5 -mr-1.5 -mt-1 text-white/40 hover:text-white/80 transition-colors"
        aria-label="Close"
      >
        <X className="h-4 w-4 md:h-[18px] md:w-[18px]" />
      </button>
    </div>
  );
}

function Dot() {
  return <span className="text-white/30 select-none">·</span>;
}

function Badge({ children }: { children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-sm border border-white/15 px-1.5 md:px-2 py-0.5 text-[10px] md:text-xs text-white/50 font-data-mono whitespace-nowrap">
      {children}
    </span>
  );
}
