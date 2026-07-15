"use client";

import { useState } from "react";
import { BookmarkPlus, X, Loader2, CheckCircle2 } from "lucide-react";
import { useCreateWeatherRecord } from "@/hooks/use-weather";
import { ApiError } from "@/lib/api-client";
import type { CurrentWeather } from "@/lib/types";

interface Props {
  locationName: string;
  latitude: number;
  longitude: number;
  countryCode?: string | null;
  weather: CurrentWeather;
}

export function SaveToHistoryButton({ locationName, latitude, longitude, countryCode, weather }: Props) {
  const [open, setOpen] = useState(false);
  const [startDate, setStartDate] = useState(() => new Date().toISOString().slice(0, 10));
  const [endDate, setEndDate] = useState(() =>
    new Date(Date.now() + 86400000).toISOString().slice(0, 10)
  );
  const { mutate, isPending, isSuccess, error, reset } = useCreateWeatherRecord();

  const handleSave = () => {
    mutate({
      location_name: locationName,
      latitude,
      longitude,
      country: countryCode,
      start_date: startDate,
      end_date: endDate,
      temperature: weather.temperature,
      humidity: weather.humidity,
      weather_condition: weather.weather_condition,
    });
  };

  return (
    <>
      <button
        onClick={() => {
          reset();
          setOpen(true);
        }}
        className="flex items-center gap-1.5 rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-ink-soft transition hover:border-sky/40 hover:text-sky"
      >
        <BookmarkPlus size={16} />
        Save to history
      </button>

      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
          onClick={() => setOpen(false)}
        >
          <div
            className="w-full max-w-sm rounded-2xl border border-border bg-surface p-5 shadow-[var(--shadow-card)]"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="font-display text-sm font-semibold text-ink">Save {locationName}</h3>
              <button onClick={() => setOpen(false)} className="text-ink-faint hover:text-ink">
                <X size={18} />
              </button>
            </div>

            {isSuccess ? (
              <div className="mt-4 flex items-center gap-2 rounded-xl bg-teal-soft p-3 text-sm text-teal">
                <CheckCircle2 size={16} />
                Saved! View it in your history.
              </div>
            ) : (
              <>
                <div className="mt-4 space-y-3">
                  <label className="block text-xs text-ink-soft">
                    Start date
                    <input
                      type="date"
                      value={startDate}
                      onChange={(e) => setStartDate(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-ink"
                    />
                  </label>
                  <label className="block text-xs text-ink-soft">
                    End date
                    <input
                      type="date"
                      value={endDate}
                      onChange={(e) => setEndDate(e.target.value)}
                      className="mt-1 w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-ink"
                    />
                  </label>
                </div>

                {error && (
                  <p className="mt-3 text-xs text-rose">
                    {error instanceof ApiError ? error.message : "Couldn't save this record."}
                  </p>
                )}

                <button
                  onClick={handleSave}
                  disabled={isPending}
                  className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-sky py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50"
                >
                  {isPending && <Loader2 size={16} className="animate-spin" />}
                  Save record
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
