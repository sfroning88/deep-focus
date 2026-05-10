"use server";

import { z } from "zod";
import { selfUserAction } from "@focus/auth/server";
import { PredictionType, TrainingType } from "@focus/db";
import { PredictionService } from "@lib/services";
import type { ModelPredictControllablePrdResponse } from "@focus/types";

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

const givePredictionFeedbackSchema = z.object({
  type: z.nativeEnum(PredictionType),
  modelType: z.nativeEnum(TrainingType),
  modelBatchId: z.string(),
  propertyId: z.string(),
  feedbackScore: z.number().min(0).max(1),
});

export const givePredictionFeedbackAction = selfUserAction(
  givePredictionFeedbackSchema,
  async (ctx): Promise<void> => {
    await predictionService.givePredictionFeedback(
      ctx.type,
      ctx.modelType,
      ctx.modelBatchId,
      ctx.propertyId,
      ctx.feedbackScore,
    );
  },
);
