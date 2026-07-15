"use client";

import { useState } from "react";
import Link from "next/link";
import { CloudSun, History, Info } from "lucide-react";
import { SearchBar } from "@/components/search-bar";
import { DarkModeToggle } from "@/components/dark-mode-toggle";
import { CurrentWeatherCard } from "@/components/current-weather-card";
import { ForecastGrid } from "@/components/forecast-grid";
import { InfoBadges } from "@/components/info-badges";
import { MapPanel } from "@/components/map-panel";
import { AssistantPanel } from "@/components/assistant-panel";
import { SaveToHistoryButton } from "@/components/save-to-history-button";
import { ErrorBanner } from "@/components/error-banner";
import { WeatherCardSkeleton, ForecastSkeleton } from "@/components/skeletons";
import { useCurrentWeather, useForecast, useGeocode } from "@/hooks/use-weather";

export default function Home() {
  const [query, setQuery] = useState<string | null>(null);
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null);
  const [coordsLabel, setCoordsLabel] = useState<string>("Current location");

  const shouldGeocode = Boolean(query) && !coords;
  const geocode = useGeocode(query ?? "", shouldGeocode);

  const activeLat = coords?.lat ?? geocode.data?.latitude;
  const activeLon = coords?.lon ?? geocode.data?.longitude;
  const activeName = coords ? coordsLabel : geocode.data?.name ?? query ?? "";

  const current = useCurrentWeather(activeLat, activeLon);
  const forecast = useForecast(activeLat, activeLon);

  const handleSearch = (q: string) => {
    const coordMatch = q.match(/^\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*$/);
    if (coordMatch) {
      setQuery(null);
      setCoordsLabel(`${coordMatch[1]}, ${coordMatch[2]}`);
      setCoords({ lat: parseFloat(coordMatch[1]), lon: parseFloat(coordMatch[2]) });
      return;
    }
    setCoords(null);
    setQuery(q);
  };

  const handleUseCurrentLocation = (lat: number, lon: number) => {
    setQuery(null);
    setCoordsLabel("Current location");
    setCoords({ lat, lon });
  };

  const topLevelError = geocode.error || current.error;
  const hasResult = Boolean(activeLat !== undefined && activeLon !== undefined);

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-surface">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
          <div className="flex items-center gap-2">
            <CloudSun size={22} className="text-sky" />
            <span className="font-display text-lg font-semibold tracking-tight">Skyline</span>
          </div>
          <div className="flex items-center gap-2">
            <Link
              href="/history"
              className="flex items-center gap-1.5 rounded-xl border border-border bg-surface px-3 py-2 text-sm text-ink-soft transition hover:text-sky"
            >
              <History size={16} />
              <span className="hidden sm:inline">History</span>
            </Link>
            <DarkModeToggle />
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <SearchBar
          onSearch={handleSearch}
          onUseCurrentLocation={handleUseCurrentLocation}
          isLoading={geocode.isFetching}
        />

        <div className="mt-6 space-y-6">
          {topLevelError ? (
            <ErrorBanner error={topLevelError} />
          ) : !hasResult ? (
            <div className="rounded-2xl border border-dashed border-border bg-surface/50 p-10 text-center text-ink-faint">
              Search for a city, zip code, or coordinates — or use your current location — to see
              live conditions.
            </div>
          ) : (
            <>
              {current.isLoading ? (
                <WeatherCardSkeleton />
              ) : current.data ? (
                <div className="space-y-3">
                  <CurrentWeatherCard locationName={activeName} weather={current.data} />
                  <div className="flex justify-end">
                    <SaveToHistoryButton
                      locationName={activeName}
                      latitude={activeLat as number}
                      longitude={activeLon as number}
                      countryCode={geocode.data?.country}
                      weather={current.data}
                    />
                  </div>
                </div>
              ) : null}

              <InfoBadges lat={activeLat} lon={activeLon} countryCode={geocode.data?.country} />

              {forecast.isLoading ? (
                <ForecastSkeleton />
              ) : forecast.data ? (
                <ForecastGrid days={forecast.data} />
              ) : forecast.error ? (
                <ErrorBanner error={forecast.error} />
              ) : null}

              <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
                <MapPanel
                  lat={activeLat as number}
                  lon={activeLon as number}
                  locationName={activeName}
                />
                <AssistantPanel lat={activeLat} lon={activeLon} locationName={activeName} />
              </div>
            </>
          )}
        </div>

        <footer className="mt-12 rounded-2xl border border-border bg-surface p-5 text-xs leading-relaxed text-ink-faint">
          <div className="flex items-start gap-2">
            <Info size={14} className="mt-0.5 shrink-0" />
            <p>
              <strong className="text-ink-soft">Built by Ramakrishna</strong> for the{" "}
              <strong className="text-ink-soft">Product Manager Accelerator (PM Accelerator)</strong>{" "}
              AI Engineer Intern technical assessment. PM Accelerator supports professionals
              through every stage of the product management lifecycle — from aspiring PMs to
              experienced leaders — through hands-on training, mentorship, and real-world project
              experience. Learn more on their LinkedIn page:{" "}
              <em>&quot;Product Manager Accelerator.&quot;</em>
            </p>
          </div>
        </footer>
      </main>
    </div>
  );
}
