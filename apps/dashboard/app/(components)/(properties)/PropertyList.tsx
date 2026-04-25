"use client";

import { useState } from "react";
import { useMediaQuery } from "@/app/(hooks)/use-media-query";
import { useFetchProperties } from "@/app/(hooks)/use-fetch-properties";
import { useUserId } from "@/app/(hooks)/use-user-id";
import { PropertyCard } from "@/app/(components)/(properties)/PropertyCard";
import { MOBILE_BREAKPOINT } from "@/lib/constants";
import type { Property } from "@focus/types";

type PropertyListProps = {
  initialData?: Property[];
};

export function PropertyList({ initialData }: PropertyListProps) {
  const userId = useUserId();
  const isMobile = !useMediaQuery(`(min-width: ${MOBILE_BREAKPOINT}px)`, true);
  const [detailId, setDetailId] = useState<string | null>(null);

  const {
    data: properties,
    isLoading: listLoading,
    isError: listError,
    error: listErrorObj,
  } = useFetchProperties(userId, initialData);

  const padding = isMobile ? "0.75rem" : "1.25rem";

  return (
    <div
      className={`space-y-4 ${isMobile ? "text-xs" : "text-sm"}`}
      style={{ padding }}
    >
      <h1
        className={`font-semibold text-slate-900 ${isMobile ? "text-lg" : "text-2xl"}`}
      >
        Properties
      </h1>

      {listLoading ? (
        <p className="text-slate-600">Loading properties…</p>
      ) : listError ? (
        <p className="text-red-700">
          {listErrorObj instanceof Error
            ? listErrorObj.message
            : "Could not load properties."}
        </p>
      ) : !properties?.length ? (
        <p className="text-slate-600">No properties to show.</p>
      ) : (
        <ul className="divide-y divide-slate-200 border border-slate-200 rounded-lg overflow-hidden bg-white">
          {properties.map((p) => (
            <li
              key={p.id}
              className="flex items-center justify-between gap-3 px-4 py-3"
            >
              <div className="min-w-0">
                <p
                  className={`font-medium text-slate-900 truncate ${isMobile ? "text-sm" : "text-base"}`}
                >
                  {p.name}
                </p>
                <p className="text-slate-600 truncate">
                  {p.city}, {p.state}
                </p>
              </div>
              <button
                type="button"
                onClick={() => setDetailId(p.id)}
                className="shrink-0 px-3 py-1.5 border-2 border-slate-400 bg-white hover:bg-slate-50 font-medium text-slate-800 rounded"
              >
                View
              </button>
            </li>
          ))}
        </ul>
      )}

      <PropertyCard
        userId={userId}
        propertyId={detailId}
        onClose={() => setDetailId(null)}
      />
    </div>
  );
}
