import "server-only";

import { db } from "@focus/db";
import type {
  ModelTrainControllablePrdResponse,
  TrainingBatchListEntry,
} from "@focus/types";
import { AIWorkerService } from "@focus/services";

export class TrainingService {
  private workerService: AIWorkerService;
  constructor() {
    this.workerService = AIWorkerService.fromEnvironment();
  }

  async trainControllablePrd(): Promise<ModelTrainControllablePrdResponse> {
    return this.workerService.modelTrainControllablePrd();
  }

  async fetchBatches(): Promise<TrainingBatchListEntry[]> {
    const batches = await db.trainingBatch.findMany({
      include: {
        models: {
          select: {
            type: true,
            status: true,
            r2score: true,
            winner: true,
          },
        },
      },
      orderBy: { createdAt: "desc" },
    });
    return batches;
  }
}
