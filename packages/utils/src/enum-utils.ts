import { PredictionType } from "@focus/db/enums";

const PREDICTION_TYPE_API_PATH: Record<PredictionType, string> = {
  [PredictionType.controllablePrd]: "controllable_prd",
  [PredictionType.occupancy]: "occupancy",
  [PredictionType.operatingMargin]: "operating_margin",
};

export function predictionTypeToApiPath(type: PredictionType): string {
  return PREDICTION_TYPE_API_PATH[type];
}
