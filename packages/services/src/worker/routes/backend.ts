import { env } from "@focus/config";
import {
  WORKER_API_ROUTES,
  type ModelPredictControllablePrdRequest,
  type ModelPredictControllablePrdResponse,
} from "@focus/types";
import { WorkerService } from "../worker-service";

export class BackendWorkerService extends WorkerService {
  static fromEnvironment(): BackendWorkerService {
    const baseUrl = env.BACKEND_API_URL ?? "";
    const authToken = env.AUTH_TOKEN ?? "";
    if (!baseUrl || !authToken) {
      console.warn(
        "BackendWorkerService: BACKEND_API_URL or AUTH_TOKEN is missing",
      );
    }
    return new BackendWorkerService({ baseUrl, authToken, timeout: 300000 });
  }

  async modelPredictControllablePrd(
    request: ModelPredictControllablePrdRequest,
  ): Promise<ModelPredictControllablePrdResponse> {
    const endpoint = `${this.config.baseUrl}${WORKER_API_ROUTES.modelPredictControllablePrd()}`;
    return this.makeRequest<ModelPredictControllablePrdResponse>(endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        property_id: request.propertyId,
        multi_enabled: request.multiEnabled,
      }),
    });
  }
}
