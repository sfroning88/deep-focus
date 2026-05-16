import "server-only";

import { db, TrainingFunction } from "@focus/db";
import type {
  ModelShuffleTrainingGroupsResponse,
  ModelTrainControllablePrdResponse,
  TrainingBatchListEntry,
  TrainingFunctionCounts,
} from "@focus/types";
import { AIWorkerService } from "@focus/services";

export class TrainingService {
  private workerService: AIWorkerService;
  constructor() {
    this.workerService = AIWorkerService.fromEnvironment();
  }

  async shuffleTrainingGroups(): Promise<ModelShuffleTrainingGroupsResponse> {
    return this.workerService.modelShuffleTrainingGroups();
  }

  async trainControllablePrd(): Promise<ModelTrainControllablePrdResponse> {
    return this.workerService.modelTrainControllablePrd();
  }

  async fetchFunctionCounts(): Promise<TrainingFunctionCounts> {
    const rows = await db.propertySnapshot.groupBy({
      by: ["function"],
      _count: { function: true },
    });
    const counts: TrainingFunctionCounts = {
      train: 0,
      validate: 0,
      test: 0,
      unassigned: 0,
    };
    for (const row of rows) {
      if (row.function === TrainingFunction.train)
        counts.train = row._count.function;
      else if (row.function === TrainingFunction.validate)
        counts.validate = row._count.function;
      else if (row.function === TrainingFunction.test)
        counts.test = row._count.function;
      else counts.unassigned = row._count.function;
    }
    return counts;
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
