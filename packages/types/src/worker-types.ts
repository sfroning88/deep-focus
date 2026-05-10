import { createRoute } from "./route-types";
import { Prediction } from "./prediction-types";

export type WorkerServiceConfig = {
  baseUrl: string;
  authToken: string;
  timeout?: number;
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
  // ai
  modelTrainControllablePrd: createRoute("/api/train/controllable_prd"),

  // backend
  modelPredictControllablePrd: createRoute("/api/predict/controllable_prd"),
};
