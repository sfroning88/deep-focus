import "server-only";

import { db } from "@focus/db";
import type {
  PredictionType,
  TrainingType,
  ModelPredictControllablePrdRequest,
  ModelPredictControllablePrdResponse,
} from "@focus/types";
import { BackendWorkerService } from "@focus/services";

export class PredictionService {
  private workerService: BackendWorkerService;
  constructor() {
    this.workerService = BackendWorkerService.fromEnvironment();
  }

  async predictControllablePrd(
    args: ModelPredictControllablePrdRequest,
  ): Promise<ModelPredictControllablePrdResponse> {
    return this.workerService.modelPredictControllablePrd(args);
  }

  async givePredictionFeedback(
    type: PredictionType,
    modelType: TrainingType,
    modelBatchId: string,
    propertyId: string,
    feedbackScore: number,
  ): Promise<void> {
    await db.prediction.update({
      data: { feedbackScore },
      where: {
        type_modelType_modelBatchId_propertyId: {
          type,
          modelType,
          modelBatchId,
          propertyId,
        },
      },
    });
  }
}
