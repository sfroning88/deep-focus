"use client";

import { SectionLabel, ValueBox, DeltaBox } from "@focus/ui";
import { toNum } from "@focus/utils";
import { usePredictControllablePrd } from "@/app/(hooks)/use-predict-controllable-prd";
import { PredictFeedback } from "./PredictFeedback";

type PredictPrdCardProps = {
  userId: string;
  propertyId: string;
  currentPrd: number | null;
};

export function PredictPrdCard({
  userId,
  propertyId,
  currentPrd,
}: PredictPrdCardProps) {
  const { mutate, data, isPending, isError, error, isSuccess, reset } =
    usePredictControllablePrd(userId);

  const predicted =
    isSuccess && data.predictions.length > 0
      ? toNum(data.predictions[0]!.result)
      : null;

  const delta =
    predicted != null && currentPrd != null ? predicted - currentPrd : null;

  return (
    <div className="border border-white/10 rounded-sm p-3 md:p-4">
      <div className="flex items-center justify-between gap-2">
        <SectionLabel>AI Prediction — Controllable PRD</SectionLabel>
        <button
          type="button"
          disabled={isPending}
          onClick={() => {
            reset();
            mutate({ propertyId });
          }}
          className={`
            rounded-md border font-data font-medium transition-colors shrink-0
            px-2.5 py-1 text-[10px] md:px-3 md:py-1.5 md:text-xs
            ${
              isPending
                ? "border-white/10 bg-white/2 text-white/30 cursor-not-allowed"
                : "border-fhp-blue-500 bg-fhp-blue-800/50 text-white hover:bg-fhp-blue-700/60"
            }
          `}
        >
          {isPending ? "Predicting…" : isSuccess ? "Re-predict" : "Predict"}
        </button>
      </div>

      {isError && (
        <p className="mt-2 text-red-400 text-xs">
          {error instanceof Error ? error.message : "Prediction failed."}
        </p>
      )}

      <div
        className={`mt-2.5 md:mt-3 grid gap-2 md:gap-3 ${
          currentPrd != null ? "grid-cols-3" : "grid-cols-1"
        }`}
      >
        {currentPrd != null && <ValueBox label="Actual" value={currentPrd} />}

        {predicted != null ? (
          <>
            <ValueBox label="Predicted" value={predicted} highlight />
            {delta != null && <DeltaBox delta={delta} baseline={currentPrd} />}
          </>
        ) : (
          <div
            className={`rounded-sm px-2 md:px-4 py-2.5 md:py-3 text-center bg-white/3 border border-white/10 ${
              currentPrd != null ? "col-span-2" : ""
            }`}
          >
            <p className="min-h-6 md:min-h-8 flex items-center justify-center">
              <span className="text-[10px] md:text-xs text-white/30">
                {isPending ? "Running model…" : "No prediction yet"}
              </span>
            </p>
            <p className="mt-0.5 text-[9px] md:text-[11px] text-white/40">
              Predicted PRD
            </p>
          </div>
        )}
      </div>

      {isSuccess && data.predictions[0] ? (
        <PredictFeedback
          userId={userId}
          propertyId={propertyId}
          type={data.predictions[0].type}
          modelType={data.predictions[0].modelType}
          modelBatchId={data.predictions[0].modelBatchId}
          feedbackScore={
            data.predictions[0].feedbackScore != null
              ? toNum(data.predictions[0].feedbackScore)
              : null
          }
        />
      ) : null}
    </div>
  );
}
