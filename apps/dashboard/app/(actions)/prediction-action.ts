"use server";

import { z } from "zod";
import { selfUserAction } from "@focus/auth/server";
import { PredictionType, TrainingType } from "@focus/db";
import { PredictionService } from "@lib/services";
import type { ModelPredictResponse } from "@focus/types";

const predictionService = new PredictionService();

const predictModelsSchema = z.object({
  predictionType: z.nativeEnum(PredictionType),
  propertyId: z.string(),
  multiEnabled: z.boolean().default(false),
});

export const predictModelsAction = selfUserAction(
  predictModelsSchema,
  async (ctx): Promise<ModelPredictResponse> => {
    return await predictionService.predict(ctx.predictionType, {
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
