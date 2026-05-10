import { env } from "@focus/config";
import {
  WORKER_API_ROUTES,
  type ModelTrainControllablePrdResponse,
} from "@focus/types";
import { WorkerService } from "../worker-service";

export class AIWorkerService extends WorkerService {
  static fromEnvironment(): AIWorkerService {
    const baseUrl = env.AI_API_URL;
    const authToken = env.AUTH_TOKEN;
    if (!baseUrl || !authToken) {
      throw new Error("Worker configuration missing");
    }
    return new AIWorkerService({
      baseUrl,
      authToken,
      timeout: 300000,
    });
  }

  async modelTrainControllablePrd(): Promise<ModelTrainControllablePrdResponse> {
    const endpoint = `${this.config.baseUrl}${WORKER_API_ROUTES.modelTrainControllablePrd()}`;
    return this.makeRequest<ModelTrainControllablePrdResponse>(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
  }
}
