export function toNum(value: unknown): number {
  if (value == null) return 0;
  if (typeof value === "number") return value;
  if (typeof value === "string") return parseFloat(value) || 0;
  if (typeof value === "object" && "toNumber" in value) {
    return (value as { toNumber: () => number }).toNumber();
  }
  return Number(value) || 0;
}

export function formatDecimal(value: unknown): string {
  if (value == null) return "—";
  if (typeof value === "number") return value.toLocaleString();
  return String(value);
}

export function formatCurrency(value: unknown): string {
  const n = toNum(value);
  return n.toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  });
}

export function formatCompactCurrency(value: unknown): string {
  const n = toNum(value);
  if (Math.abs(n) >= 1_000_000) {
    return `$${(n / 1_000_000).toFixed(2)}M`;
  }
  if (Math.abs(n) >= 1_000) {
    return `$${(n / 1_000).toFixed(0)}K`;
  }
  return formatCurrency(value);
}

export function formatPercent(value: unknown): string {
  const n = toNum(value);
  return `${n.toFixed(2)}%`;
}

export type OccupancyTier = "high" | "mid" | "low";

export function getOccupancyTier(occ: unknown): OccupancyTier {
  const n = toNum(occ);
  if (n >= 80) return "high";
  if (n >= 65) return "mid";
  return "low";
}

export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("en-US", {
    month: "2-digit",
    day: "2-digit",
    year: "numeric",
  });
}

export type SortField = "name" | "msa" | "occupancy";
export type SortDir = "asc" | "desc";
