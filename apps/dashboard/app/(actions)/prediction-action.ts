"use server";

import { z } from "zod";
import { selfUserAction } from "@focus/auth/server";
import { PredictionService } from "@lib/services";
import { type ModelPredictControllablePrdResponse } from "@focus/types";

const predictionService = new PredictionService();

const predictControllablePrdSchema = z.object({
  propertyId: z.string(),
  multiEnabled: z.boolean().default(false),
});

export const predictControllablePrdAction = selfUserAction(
  predictControllablePrdSchema,
  async (ctx): Promise<ModelPredictControllablePrdResponse> => {
    return await predictionService.predictControllablePrd({
      propertyId: ctx.propertyId,
      multiEnabled: ctx.multiEnabled || false,
    });
  },
);
