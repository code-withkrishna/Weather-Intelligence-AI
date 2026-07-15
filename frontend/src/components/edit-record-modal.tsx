"use client";

import { useState } from "react";
import { X, Loader2 } from "lucide-react";
import { useUpdateWeatherRecord } from "@/hooks/use-weather";
import { ApiError } from "@/lib/api-client";
import type { WeatherRecord } from "@/lib/types";

export function EditRecordModal({
  record,
  onClose,
}: {
  record: WeatherRecord;
  onClose: () => void;
}) {
  const [startDate, setStartDate] = useState(record.start_date);
  const [endDate, setEndDate] = useState(record.end_date);
  const [temperature, setTemperature] = useState(record.temperature?.toString() ?? "");
  const [condition, setCondition] = useState(record.weather_condition ?? "");
  const { mutate, isPending, error } = useUpdateWeatherRecord();

  const handleSave = () => {
    mutate(
      {
        id: record.id,
        changes: {
          start_date: startDate,
          end_date: endDate,
          temperature: temperature ? parseFloat(temperature) : null,
          weather_condition: condition || null,
        },
      },
      { onSuccess: onClose }
    );
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4" onClick={onClose}>
      <div
        className="w-full max-w-sm rounded-2xl border border-border bg-surface p-5 shadow-[var(--shadow-card)]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between">
          <h3 className="font-display text-sm font-semibold text-ink">
            Edit {record.location_name}
          </h3>
          <button onClick={onClose} className="text-ink-faint hover:text-ink">
            <X size={18} />
          </button>
        </div>

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
          <label className="block text-xs text-ink-soft">
            Temperature (°C)
            <input
              type="number"
              step="0.1"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-ink"
            />
          </label>
          <label className="block text-xs text-ink-soft">
            Condition
            <input
              type="text"
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              className="mt-1 w-full rounded-lg border border-border bg-canvas px-3 py-2 text-sm text-ink"
            />
          </label>
        </div>

        {error && (
          <p className="mt-3 text-xs text-rose">
            {error instanceof ApiError ? error.message : "Couldn't update this record."}
          </p>
        )}

        <button
          onClick={handleSave}
          disabled={isPending}
          className="mt-4 flex w-full items-center justify-center gap-2 rounded-xl bg-sky py-2.5 text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50"
        >
          {isPending && <Loader2 size={16} className="animate-spin" />}
          Save changes
        </button>
      </div>
    </div>
  );
}
