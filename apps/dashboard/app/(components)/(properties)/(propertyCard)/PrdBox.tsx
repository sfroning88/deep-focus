import { formatCurrency } from "@focus/utils";

export function PrdBox({
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
