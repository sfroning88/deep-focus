import type { OccupancyTier } from "@focus/utils";

export const occupancyColors: Record<OccupancyTier, string> = {
  high: "text-white bg-green-950 border-green-700",
  mid: "text-white bg-amber-950 border-amber-700",
  low: "text-white bg-red-950 border-red-700",
} as const;
