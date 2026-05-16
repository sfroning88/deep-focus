"use server";

import { z } from "zod";
import { platformAdminAction } from "@focus/auth/server";
import { TrainingService } from "@lib/services";
import {
  type TrainingBatchListEntry,
  type TrainingFunctionCounts,
  type ModelTrainControllablePrdResponse,
  ModelShuffleTrainingGroupsResponse,
} from "@focus/types";

const trainingService = new TrainingService();

const shuffleTrainingGroupsSchema = z.object({});

export const shuffleTrainingGroupsAction = platformAdminAction(
  shuffleTrainingGroupsSchema,
  async (): Promise<ModelShuffleTrainingGroupsResponse> => {
    return await trainingService.shuffleTrainingGroups();
  },
);

const trainControllablePrdSchema = z.object({});

export const trainControllablePrdAction = platformAdminAction(
  trainControllablePrdSchema,
  async (): Promise<ModelTrainControllablePrdResponse> => {
    return await trainingService.trainControllablePrd();
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
