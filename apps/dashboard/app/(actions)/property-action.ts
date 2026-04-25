"use server";

import { z } from "zod";
import { selfUserAction } from "@focus/auth/server";
import { PropertyService } from "@lib/services/src/property/server/property-service";
import { Property, PropertyCard } from "@focus/types";

const fetchPropertiesSchema = z.object({});

export const fetchPropertiesAction = selfUserAction(
  fetchPropertiesSchema,
  async (): Promise<Property[]> => {
    return await PropertyService.fetchProperties();
  },
);

const fetchPropertyCardSchema = z.object({
  id: z.string(),
});

export const fetchPropertyCardAction = selfUserAction(
  fetchPropertyCardSchema,
  async (ctx): Promise<PropertyCard> => {
    return await PropertyService.fetchPropertyCard(ctx.id);
  },
);
