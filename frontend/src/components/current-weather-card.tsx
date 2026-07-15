"use client";

import { Droplets, Eye, Gauge, Wind, Sunrise, Sunset, Sun as SunIcon } from "lucide-react";
import { WeatherIcon } from "@/components/weather-icon";
import { AtmosphereBar } from "@/components/atmosphere-bar";
import type { CurrentWeather } from "@/lib/types";

function Metric({
  icon,
  label,
  value,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
}) {
  return (
    <div className="flex items-center gap-2.5 rounded-lg bg-surface-muted px-3 py-2.5">
      <span className="text-ink-faint">{icon}</span>
      <div className="leading-tight">
        <p className="font-mono text-sm font-medium text-ink">{value}</p>
        <p className="text-[11px] text-ink-faint">{label}</p>
      </div>
    </div>
  );
}

export function CurrentWeatherCard({
  locationName,
  weather,
}: {
  locationName: string;
  weather: CurrentWeather;
}) {
  const tzOffset =
    typeof weather.timezone_offset === "number" ? weather.timezone_offset : 0;

  return (
    <div className="rounded-2xl border border-border bg-surface p-6 shadow-[var(--shadow-card)]">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-ink-soft">{locationName}</p>
          <p className="mt-1 font-display text-5xl font-semibold tracking-tight text-ink">
            {Math.round(weather.temperature)}°
            <span className="text-2xl font-normal text-ink-faint">C</span>
          </p>
          <p className="mt-1 text-sm capitalize text-ink-soft">
            {weather.description} · feels like {Math.round(weather.feels_like)}°
          </p>
        </div>
        <WeatherIcon icon={weather.icon} condition={weather.weather_condition} size={64} />
      </div>

      {weather.sunrise && weather.sunset && (
        <div className="mt-5">
          <AtmosphereBar
            sunrise={weather.sunrise}
            sunset={weather.sunset}
            timezoneOffsetSeconds={tzOffset}
          />
        </div>
      )}

      <div className="mt-5 grid grid-cols-2 gap-2 sm:grid-cols-3">
        <Metric icon={<Droplets size={16} />} label="Humidity" value={`${Math.round(weather.humidity)}%`} />
        <Metric icon={<Gauge size={16} />} label="Pressure" value={`${Math.round(weather.pressure)} hPa`} />
        <Metric icon={<Wind size={16} />} label="Wind" value={`${weather.wind_speed.toFixed(1)} m/s`} />
        <Metric icon={<Eye size={16} />} label="Visibility" value={`${weather.visibility.toFixed(1)} km`} />
        {weather.uv_index !== null && (
          <Metric icon={<SunIcon size={16} />} label="UV Index" value={weather.uv_index.toFixed(0)} />
        )}
        {weather.sunrise && (
          <Metric icon={<Sunrise size={16} />} label="Sunrise" value={formatTime(weather.sunrise, tzOffset)} />
        )}
        {weather.sunset && (
          <Metric icon={<Sunset size={16} />} label="Sunset" value={formatTime(weather.sunset, tzOffset)} />
        )}
      </div>
    </div>
  );
}

function formatTime(unixSeconds: number, tzOffsetSeconds: number): string {
  return new Date((unixSeconds + tzOffsetSeconds) * 1000).toLocaleTimeString(undefined, {
    hour: "numeric",
    minute: "2-digit",
    timeZone: "UTC",
  });
}
