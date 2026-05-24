"use server";

import { z } from "zod";
import { platformAdminAction } from "@focus/auth/server";
import { PredictionType } from "@focus/db";
import { TrainingService } from "@lib/services";
import {
  type TrainingBatchListEntry,
  type TrainingFunctionCounts,
  type ModelTrainingResponse,
  ModelShuffleResponse,
} from "@focus/types";

const trainingService = new TrainingService();

const shuffleGroupsSchema = z.object({});

export const shuffleGroupsAction = platformAdminAction(
  shuffleGroupsSchema,
  async (): Promise<ModelShuffleResponse> => {
    return await trainingService.shuffleGroups();
  },
);

const trainModelsSchema = z.object({
  predictionType: z.nativeEnum(PredictionType),
});

export const trainModels = platformAdminAction(
  trainModelsSchema,
  async (ctx): Promise<ModelTrainingResponse> => {
    return await trainingService.train(ctx.predictionType);
  },
);

const fetchFunctionCountsSchema = z.object({});

export const fetchFunctionCountsAction = platformAdminAction(
  fetchFunctionCountsSchema,
  async (): Promise<TrainingFunctionCounts> => {
    return await trainingService.fetchFunctionCounts();
  },
);

const fetchBatchesSchema = z.object({});

export const fetchBatchesAction = platformAdminAction(
  fetchBatchesSchema,
  async (): Promise<TrainingBatchListEntry[]> => {
    return await trainingService.fetchBatches();
  },
);
