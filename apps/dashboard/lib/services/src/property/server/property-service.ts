import "server-only";

import { db } from "@focus/db";
import {
  type CreateSnapshotArgs,
  type PropertyCard,
  type PropertyListEntry,
  type PropertySnapshot,
} from "@focus/types";

export const PropertyService = {
  async fetchProperties(): Promise<PropertyListEntry[]> {
    const properties = await db.property.findMany({
      orderBy: { name: "asc" },
      include: {
        msa: { select: { name: true } },
        snapshots: {
          orderBy: { reportedAt: "desc" },
          take: 1,
          select: { occupancy: true },
        },
        _count: { select: { snapshots: true } },
      },
    });
    if (!properties || properties.length === 0) {
      throw new Error("No properties were found");
    }
    return properties;
  },

  async fetchPropertyCard(id: string): Promise<PropertyCard> {
    const property = await db.property.findUnique({
      where: { id },
      include: { snapshots: true, msa: true },
    });
    if (!property) {
      throw new Error("Property does not exist");
    }
    return property;
  },

  async createSnapshot(args: CreateSnapshotArgs): Promise<PropertySnapshot> {
    const property = await db.property.findUnique({
      where: { id: args.propertyId },
    });
    if (!property) {
      throw new Error("Property does not exist");
    }
    const { propertyId, reportedAt: reportedAtRaw, ...metrics } = args;
    const reportedAt = new Date(reportedAtRaw);
    if (Number.isNaN(reportedAt.getTime())) {
      throw new Error("Invalid reportedAt date");
    }
    return db.propertySnapshot.upsert({
      where: {
        propertyId_reportedAt: { propertyId, reportedAt },
      },
      create: {
        propertyId,
        reportedAt,
        ...metrics,
      },
      update: metrics,
    });
  },
};
