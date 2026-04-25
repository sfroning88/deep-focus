"use client";

import { createPortal } from "react-dom";
import { useFetchPropertyCard } from "@/app/(hooks)/use-fetch-property-card";
import { useMediaQuery } from "@/app/(hooks)/use-media-query";
import { MOBILE_BREAKPOINT } from "@/lib/constants";
import { formatDecimal } from "@focus/utils";

type PropertyCardProps = {
  userId: string;
  propertyId: string | null;
  onClose: () => void;
};

export function PropertyCard({
  userId,
  propertyId,
  onClose,
}: PropertyCardProps) {
  const isMobile = !useMediaQuery(`(min-width: ${MOBILE_BREAKPOINT}px)`, true);
  const {
    data: card,
    isLoading: cardLoading,
    isError: cardError,
    error: cardErrorObj,
  } = useFetchPropertyCard(userId, propertyId);

  const padding = isMobile ? "0.75rem" : "1.25rem";
  const textSm = isMobile ? "text-xs" : "text-sm";
  const textBase = isMobile ? "text-sm" : "text-base";

  if (propertyId == null) {
    return null;
  }

  const modal = (
    <>
      <div
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onClose}
        aria-hidden
      />
      <div
        className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 bg-white border-4 border-slate-400 shadow-lg z-50 flex flex-col gap-4 overflow-hidden max-w-3xl max-h-[85vh] w-[92vw]"
        style={{ padding }}
      >
        <div className="flex items-center justify-between flex-shrink-0 gap-2">
          <h2
            className={`font-semibold truncate ${isMobile ? "text-base" : "text-xl"}`}
          >
            {cardLoading ? "Loading…" : (card?.name ?? "Property details")}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className={`text-slate-600 hover:text-slate-800 leading-none shrink-0 ${isMobile ? "text-xl" : "text-2xl"}`}
            aria-label="Close"
          >
            ×
          </button>
        </div>
        {cardError ? (
          <p className={`text-red-700 ${textSm}`}>
            {cardErrorObj instanceof Error
              ? cardErrorObj.message
              : "Could not load property details."}
          </p>
        ) : card ? (
          <div
            className={`overflow-auto flex-1 flex flex-col gap-4 min-h-0 ${textSm}`}
          >
            <section className="space-y-1">
              <h3 className={`font-medium text-slate-800 ${textBase}`}>
                Location
              </h3>
              <p>
                {card.address}, {card.city}, {card.state} {card.zip}
              </p>
            </section>
            <section className="space-y-1">
              <h3 className={`font-medium text-slate-800 ${textBase}`}>
                NIC MSA
              </h3>
              <p>
                <span className="font-medium">{card.msa.name}</span>
                <span className="text-slate-600">
                  {" "}
                  · population {card.msa.population.toLocaleString()}
                </span>
              </p>
            </section>
            <section className="space-y-2 min-h-0 flex flex-col">
              <h3 className={`font-medium text-slate-800 shrink-0 ${textBase}`}>
                Snapshots
              </h3>
              {card.snapshots.length === 0 ? (
                <p className="text-slate-600">No snapshots on file.</p>
              ) : (
                <div className="overflow-auto border border-slate-200 rounded">
                  <table className="w-full text-left border-collapse">
                    <thead className="bg-slate-50 sticky top-0">
                      <tr>
                        <th
                          className={`p-2 font-medium border-b border-slate-200 ${textSm}`}
                        >
                          Reported
                        </th>
                        <th
                          className={`p-2 font-medium border-b border-slate-200 ${textSm}`}
                        >
                          Occupancy %
                        </th>
                        <th
                          className={`p-2 font-medium border-b border-slate-200 ${textSm}`}
                        >
                          Total revenues
                        </th>
                        <th
                          className={`p-2 font-medium border-b border-slate-200 ${textSm}`}
                        >
                          Op. margin %
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...card.snapshots]
                        .sort(
                          (a, b) =>
                            new Date(b.reportedAt).getTime() -
                            new Date(a.reportedAt).getTime(),
                        )
                        .map((s) => (
                          <tr
                            key={`${card.id}-${s.reportedAt.toISOString()}`}
                            className="border-b border-slate-100 last:border-0"
                          >
                            <td className="p-2 whitespace-nowrap">
                              {new Date(s.reportedAt).toLocaleDateString()}
                            </td>
                            <td className="p-2">
                              {formatDecimal(s.occupancy)}
                            </td>
                            <td className="p-2">
                              {formatDecimal(s.totalRevenues)}
                            </td>
                            <td className="p-2">
                              {formatDecimal(s.operatingMargin)}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </section>
          </div>
        ) : null}
      </div>
    </>
  );

  return typeof window !== "undefined"
    ? createPortal(modal, document.body)
    : null;
}
