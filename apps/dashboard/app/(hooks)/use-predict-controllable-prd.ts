"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import posthog from "posthog-js";
import { POSTHOG_EVENTS } from "@focus/types";
import { predictControllablePrdAction } from "../(actions)/prediction-action";
import { QUERY_KEYS } from "@/lib/constants";

type PredictArgs = {
  propertyId: string;
  multiEnabled?: boolean;
};

export function usePredictControllablePrd(userId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (args: PredictArgs) =>
      predictControllablePrdAction({
        propertyId: args.propertyId,
        multiEnabled: args.multiEnabled ?? false,
      }),
    onSuccess: async (data, args) => {
      posthog.capture(POSTHOG_EVENTS.model_prediction_requested, {
        property_id: args.propertyId,
        multi_enabled: args.multiEnabled ?? false,
        prediction_count: data.predictions.length,
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
