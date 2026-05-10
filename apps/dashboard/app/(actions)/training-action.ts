"use server";

import { z } from "zod";
import { platformAdminAction } from "@focus/auth/server";
import { TrainingService } from "@lib/services";
import {
  type TrainingBatchListEntry,
  type ModelTrainControllablePrdResponse,
} from "@focus/types";

const trainingService = new TrainingService();

const trainControllablePrdSchema = z.object({});

export const trainControllablePrdAction = platformAdminAction(
  trainControllablePrdSchema,
  async (): Promise<ModelTrainControllablePrdResponse> => {
    return await trainingService.trainControllablePrd();
  },
);

const fetchBatchesSchema = z.object({});

export const fetchBatchesAction = platformAdminAction(
  fetchBatchesSchema,
  async (): Promise<TrainingBatchListEntry[]> => {
    return await trainingService.fetchBatches();
  },
);
