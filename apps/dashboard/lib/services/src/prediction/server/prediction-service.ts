import "server-only";

import { db } from "@focus/db";
import type {
  Prediction,
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
    const response = await this.workerService.modelPredictControllablePrd(args);
    await this.persistPredictions(response.predictions);
    return response;
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

  private async persistPredictions(predictions: Prediction[]): Promise<void> {
    const operations = predictions.map((p) =>
      db.prediction.upsert({
        where: {
          type_modelType_modelBatchId_propertyId: {
            type: p.type,
            modelType: p.modelType,
            modelBatchId: p.modelBatchId,
            propertyId: p.propertyId,
          },
        },
        update: { result: p.result },
        create: {
          type: p.type,
          result: p.result,
          modelType: p.modelType,
          modelBatchId: p.modelBatchId,
          propertyId: p.propertyId,
        },
      }),
    );
    await db.$transaction(operations);
  }
}
