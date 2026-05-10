import "server-only";

import type {
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
}
