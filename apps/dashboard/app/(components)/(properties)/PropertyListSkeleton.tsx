export function PropertyListSkeleton() {
  return (
    <div className="space-y-4 animate-pulse" style={{ padding: "1.25rem" }}>
      <div className="h-8 w-40 rounded bg-slate-200" />
      <div className="divide-y divide-slate-200 border border-slate-200 rounded-lg overflow-hidden bg-white">
        {Array.from({ length: 5 }).map((_, i) => (
          <div
            key={i}
            className="flex items-center justify-between gap-3 px-4 py-3"
          >
            <div className="flex flex-col gap-1.5 min-w-0">
              <div className="h-4 w-48 rounded bg-slate-200" />
              <div className="h-3 w-28 rounded bg-slate-100" />
            </div>
            <div className="h-8 w-16 rounded border-2 border-slate-200 bg-slate-50" />
          </div>
        ))}
      </div>
    </div>
  );
}
