"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import posthog from "posthog-js";
import {
  PREDICTION_TYPES,
  PredictionsForProperty,
  POSTHOG_EVENTS,
} from "@focus/types";
import { predictModelsAction } from "../(actions)/prediction-action";
import { QUERY_KEYS } from "@/lib/constants";

type PredictArgs = {
  propertyId: string;
  multiEnabled?: boolean;
};

export function usePredictModels(userId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (args: PredictArgs): Promise<PredictionsForProperty> => {
      const results = await Promise.all(
        PREDICTION_TYPES.map((prediction) =>
          predictModelsAction({
            predictionType: prediction,
            propertyId: args.propertyId,
            multiEnabled: args.multiEnabled ?? false,
          }).then((response) => [prediction, response] as const),
        ),
      );
      return Object.fromEntries(results) as PredictionsForProperty;
    },
    onSuccess: async (data, args) => {
      posthog.capture(POSTHOG_EVENTS.model_prediction_requested, {
        property_id: args.propertyId,
        multi_enabled: args.multiEnabled ?? false,
        predictions_count:
          data.controllablePrd.predictions.length +
          data.occupancy.predictions.length +
          data.operatingMargin.predictions.length,
      });
      await queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.predictions(userId, args.propertyId),
      });
      await queryClient.invalidateQueries({
        queryKey: QUERY_KEYS.propertyCard(userId, args.propertyId),
      });
    },
  });
}
