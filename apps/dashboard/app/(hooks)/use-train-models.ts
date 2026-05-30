"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import posthog from "posthog-js";
import { PREDICTION_TYPES, TrainingJobs, POSTHOG_EVENTS } from "@focus/types";
import { trainModelsAction } from "../(actions)/training-action";
import { QUERY_KEYS } from "@/lib/constants";

export function useTrainModels(userId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (): Promise<TrainingJobs> => {
      const results = await Promise.all(
        PREDICTION_TYPES.map((prediction) =>
          trainModelsAction({
            predictionType: prediction,
          }),
        ),
      );
      return { jobIds: results.flatMap((response) => response.jobIds) };
    },
    onSuccess: async (data) => {
      posthog.capture(POSTHOG_EVENTS.model_training_started, {
        job_count: data.jobIds.length,
      });
      await queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.trainingBatches(userId),
      });
    },
  });
}
