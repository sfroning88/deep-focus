import { createRoute } from "./route-types";
import { Prediction } from "./prediction-types";

export type WorkerServiceConfig = {
  baseUrl: string;
  authToken: string;
  timeout?: number;
};

export type ModelShuffleTrainingGroupsResponse = {
  jobId: string;
};

export type ModelTrainControllablePrdResponse = {
  jobIds: string[];
};

export type ModelPredictControllablePrdRequest = {
  propertyId: string;
  multiEnabled: boolean;
};

export type ModelPredictControllablePrdResponse = {
  predictions: Prediction[];
};

export const WORKER_API_ROUTES = {
  // apps/ai: shuffle train/validate/test groups
  modelShuffleGroups: createRoute("/api/shuffle"),

  // apps/ai: train models on controllable prd
  modelTrainControllablePrd: createRoute("/api/train/controllable_prd"),

  // apps/backend: predict controllable prd for property
  modelPredictControllablePrd: createRoute("/api/predict/controllable_prd"),
};
