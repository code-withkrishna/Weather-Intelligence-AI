"use client";

import { Droplets, Umbrella, Wind } from "lucide-react";
import { WeatherIcon } from "@/components/weather-icon";
import type { ForecastDay } from "@/lib/types";

export function ForecastGrid({ days }: { days: ForecastDay[] }) {
  return (
    <div className="rounded-2xl border border-border bg-surface p-5 shadow-[var(--shadow-card)]">
      <h2 className="font-display text-sm font-semibold text-ink-soft">5-Day Forecast</h2>
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
        {days.slice(0, 5).map((day) => (
          <div
            key={day.date}
            className="flex flex-col items-center rounded-xl bg-surface-muted px-3 py-4 text-center"
          >
            <p className="text-xs font-medium text-ink-soft">
              {new Date(day.date).toLocaleDateString(undefined, { weekday: "short" })}
            </p>
            <WeatherIcon icon={day.icon} condition={day.weather_condition} size={32} className="my-2" />
            <p className="font-mono text-sm text-ink">
              <span className="font-semibold">{Math.round(day.temp_max)}°</span>
              <span className="text-ink-faint"> / {Math.round(day.temp_min)}°</span>
            </p>
            <div className="mt-2 flex w-full flex-col gap-1 text-[11px] text-ink-faint">
              <span className="flex items-center justify-center gap-1">
                <Umbrella size={11} /> {Math.round(day.pop)}%
              </span>
              <span className="flex items-center justify-center gap-1">
                <Droplets size={11} /> {Math.round(day.humidity)}%
              </span>
              <span className="flex items-center justify-center gap-1">
                <Wind size={11} /> {day.wind_speed.toFixed(1)} m/s
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
