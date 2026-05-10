"use client";

import { useMediaQuery } from "@/app/(hooks)/use-media-query";
import { useFetchBatches } from "@/app/(hooks)/use-fetch-batches";
import { useTrainControllablePrd } from "@/app/(hooks)/use-train-controllable-prd";
import { useUserId } from "@/app/(hooks)/use-user-id";
import { BatchListItem } from "./BatchListItem";
import { MOBILE_BREAKPOINT } from "@/lib/constants";
import type { TrainingBatchListEntry } from "@focus/types";

type BatchListProps = {
  initialData?: TrainingBatchListEntry[];
};

export function BatchList({ initialData }: BatchListProps) {
  const userId = useUserId();
  const isMobile = !useMediaQuery(`(min-width: ${MOBILE_BREAKPOINT}px)`, true);

  const {
    data: batches,
    isLoading,
    isError,
    error,
  } = useFetchBatches(userId, initialData);

  const trainMutation = useTrainControllablePrd(userId);

  return (
    <div className="space-y-4 font-data">
      <div className="flex items-center justify-between">
        <h2
          className={`font-semibold text-fhp-blue-400 ${isMobile ? "text-lg" : "text-2xl"}`}
        >
          Training Batches
        </h2>
        <button
          type="button"
          disabled={trainMutation.isPending}
          onClick={() => trainMutation.mutate()}
          className={`
            rounded-md border font-data font-medium transition-colors
            ${isMobile ? "px-3 py-1.5 text-xs" : "px-4 py-2 text-sm"}
            ${
              trainMutation.isPending
                ? "border-white/10 bg-white/[0.02] text-white/30 cursor-not-allowed"
                : "border-fhp-blue-500 bg-fhp-blue-800/50 text-white hover:bg-fhp-blue-700/60"
            }
          `}
        >
          {trainMutation.isPending ? "Training…" : "Train Models"}
        </button>
      </div>

      {trainMutation.isError && (
        <p className="text-red-400 text-sm">
          {trainMutation.error instanceof Error
            ? trainMutation.error.message
            : "Training request failed."}
        </p>
      )}

      {trainMutation.isSuccess && (
        <p className="text-green-400 text-sm">
          Training started — {trainMutation.data.jobIds.length} job(s) queued.
        </p>
      )}

      {isLoading ? (
        <p className="text-white/50 text-sm">Loading batches…</p>
      ) : isError ? (
        <p className="text-red-400 text-sm">
          {error instanceof Error
            ? error.message
            : "Could not load training batches."}
        </p>
      ) : !batches?.length ? (
        <p className="text-white/40 text-sm">
          No training batches yet. Click &ldquo;Train Models&rdquo; to start.
        </p>
      ) : (
        <>
          <ul className="border border-white/10 rounded-md overflow-hidden bg-surface-dark">
            {batches.map((b) => (
              <BatchListItem key={b.id} batch={b} isMobile={isMobile} />
            ))}
          </ul>
          <p className="text-[11px] text-white/30 font-data-mono">
            {batches.length} {batches.length === 1 ? "batch" : "batches"}
          </p>
        </>
      )}
    </div>
  );
}
