"use client";

/**
 * Signature element of the dashboard: a horizontal gradient that
 * represents the day/night arc for the searched location — dawn, day,
 * dusk, night — with a marker showing exactly where "now" falls in that
 * arc. Unlike a decorative gradient, every stop here is derived from real
 * sunrise/sunset data, so it's structure, not decoration.
 */
export function AtmosphereBar({
  sunrise,
  sunset,
  timezoneOffsetSeconds = 0,
}: {
  sunrise?: number | null;
  sunset?: number | null;
  timezoneOffsetSeconds?: number;
}) {
  if (!sunrise || !sunset) return null;

  const nowUtc = Date.now() / 1000;
  const localNow = nowUtc + timezoneOffsetSeconds;
  const dayStart = sunrise - 2 * 3600; // show some dawn buffer
  const dayEnd = sunset + 2 * 3600; // dusk buffer
  const span = dayEnd - dayStart;
  const clampedNow = Math.min(Math.max(localNow, dayStart), dayEnd);
  const markerPct = ((clampedNow - dayStart) / span) * 100;

  const sunrisePct = ((sunrise - dayStart) / span) * 100;
  const sunsetPct = ((sunset - dayStart) / span) * 100;

  const format = (ts: number) =>
    new Date(ts * 1000).toLocaleTimeString(undefined, {
      hour: "numeric",
      minute: "2-digit",
      timeZone: "UTC",
    });

  return (
    <div className="w-full">
      <div
        className="relative h-2 w-full rounded-full"
        style={{
          background:
            "linear-gradient(90deg, #1e293b 0%, #7c95c4 12%, #f3c98b 22%, #fef3c7 35%, #a9d6f5 50%, #fef3c7 65%, #f0a45e 78%, #4b5e8e 88%, #1e293b 100%)",
        }}
        role="img"
        aria-label={`Day progress: sunrise ${format(sunrise)}, sunset ${format(sunset)}`}
      >
        <div
          className="absolute -top-1.5 h-5 w-1 rounded-full bg-surface shadow-[0_0_0_2px_var(--color-ink)]"
          style={{ left: `calc(${markerPct}% - 2px)` }}
          title="Now"
        />
      </div>
      <div className="mt-1.5 flex justify-between text-[11px] font-mono text-ink-faint">
        <span style={{ marginLeft: `calc(${sunrisePct}% - 20px)` }}>↑ {format(sunrise)}</span>
        <span style={{ marginRight: `calc(${100 - sunsetPct}% - 20px)` }}>↓ {format(sunset)}</span>
      </div>
    </div>
  );
}
