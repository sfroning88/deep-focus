import {
  Prisma,
  type Property as PrismaProperty,
  type PropertySnapshot as PrismaPropertySnapshot,
} from "@focus/db";

export type Property = PrismaProperty;
export type PropertySnapshot = PrismaPropertySnapshot;

export type PropertyCard = Prisma.PropertyGetPayload<{
  include: { snapshots: true; msa: true };
}>;
