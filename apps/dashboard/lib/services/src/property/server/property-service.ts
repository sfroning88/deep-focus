import "server-only";

import { db } from "@focus/db";
import { Property, PropertyCard } from "@focus/types";

export const PropertyService = {
  async fetchProperties(): Promise<Property[]> {
    const properties = await db.property.findMany({
      orderBy: { name: "asc" },
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
};
