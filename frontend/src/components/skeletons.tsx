export function WeatherCardSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl border border-border bg-surface p-6">
      <div className="h-4 w-32 rounded bg-surface-muted" />
      <div className="mt-3 h-12 w-24 rounded bg-surface-muted" />
      <div className="mt-2 h-4 w-40 rounded bg-surface-muted" />
      <div className="mt-6 grid grid-cols-3 gap-2">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-12 rounded-lg bg-surface-muted" />
        ))}
      </div>
    </div>
  );
}

export function ForecastSkeleton() {
  return (
    <div className="animate-pulse rounded-2xl border border-border bg-surface p-5">
      <div className="h-4 w-28 rounded bg-surface-muted" />
      <div className="mt-4 grid grid-cols-5 gap-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-32 rounded-xl bg-surface-muted" />
        ))}
      </div>
    </div>
  );
}
