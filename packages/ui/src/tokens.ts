import { OccupancyTier } from "@focus/utils";

export const occupancyColors: Record<OccupancyTier, string> = {
  [OccupancyTier.high]: "text-white bg-green-950 border-green-700",
  [OccupancyTier.mid]: "text-white bg-amber-950 border-amber-700",
  [OccupancyTier.low]: "text-white bg-red-950 border-red-700",
};
