"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import posthog from "posthog-js";
import { POSTHOG_EVENTS } from "@focus/types";
import { shuffleTrainingGroupsAction } from "../(actions)/training-action";
import { QUERY_KEYS } from "@/lib/constants";

export function useShuffleTrainingGroups(userId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => shuffleTrainingGroupsAction({}),
    onSuccess: async (data) => {
      posthog.capture(POSTHOG_EVENTS.model_shuffle_training_groups, {
        job_id: data.jobId,
      });
      await Promise.all([
        queryClient.invalidateQueries({
          queryKey: QUERY_KEYS.trainingBatches(userId),
        }),
        queryClient.invalidateQueries({
          queryKey: QUERY_KEYS.trainingFunctionCounts(userId),
        }),
      ]);
    },
  });
}
