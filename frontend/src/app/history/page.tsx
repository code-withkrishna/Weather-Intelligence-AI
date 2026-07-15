"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowLeft, Pencil, Trash2, Search, Loader2 } from "lucide-react";
import { DarkModeToggle } from "@/components/dark-mode-toggle";
import { ExportMenu } from "@/components/export-menu";
import { EditRecordModal } from "@/components/edit-record-modal";
import { ErrorBanner } from "@/components/error-banner";
import { useDeleteWeatherRecord, useWeatherHistory } from "@/hooks/use-weather";
import type { WeatherRecord } from "@/lib/types";

export default function HistoryPage() {
  const [page, setPage] = useState(1);
  const [locationFilter, setLocationFilter] = useState("");
  const [debouncedFilter, setDebouncedFilter] = useState("");
  const [editing, setEditing] = useState<WeatherRecord | null>(null);
  const { data, isLoading, error } = useWeatherHistory(page, debouncedFilter || undefined);
  const deleteRecord = useDeleteWeatherRecord();

  let filterTimeout: ReturnType<typeof setTimeout>;
  const handleFilterChange = (value: string) => {
    setLocationFilter(value);
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(() => {
      setPage(1);
      setDebouncedFilter(value);
    }, 400);
  };

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete the saved weather record for ${name}?`)) {
      deleteRecord.mutate(id);
    }
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-border bg-surface">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2 text-ink-soft hover:text-sky">
            <ArrowLeft size={18} />
            <span className="font-display text-sm font-medium">Back to dashboard</span>
          </Link>
          <DarkModeToggle />
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h1 className="font-display text-2xl font-semibold tracking-tight">Weather History</h1>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search size={16} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
              <input
                value={locationFilter}
                onChange={(e) => handleFilterChange(e.target.value)}
                placeholder="Filter by location"
                className="rounded-xl border border-border bg-surface py-2 pl-9 pr-3 text-sm text-ink placeholder:text-ink-faint focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky/40"
              />
            </div>
            <ExportMenu location={debouncedFilter || undefined} />
          </div>
        </div>

        <div className="mt-6">
          {error ? (
            <ErrorBanner error={error} />
          ) : isLoading ? (
            <div className="flex justify-center py-16 text-ink-faint">
              <Loader2 size={24} className="animate-spin" />
            </div>
          ) : !data || data.items.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-surface/50 p-10 text-center text-ink-faint">
              No saved weather records yet. Search for a location on the dashboard and use
              &quot;Save to history.&quot;
            </div>
          ) : (
            <div className="overflow-hidden rounded-2xl border border-border bg-surface shadow-[var(--shadow-card)]">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="border-b border-border bg-surface-muted text-xs uppercase tracking-wide text-ink-faint">
                    <th className="px-4 py-3 font-medium">Location</th>
                    <th className="px-4 py-3 font-medium">Dates</th>
                    <th className="px-4 py-3 font-medium">Temp</th>
                    <th className="px-4 py-3 font-medium">Condition</th>
                    <th className="px-4 py-3 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {data.items.map((record) => (
                    <tr key={record.id} className="border-b border-border last:border-0">
                      <td className="px-4 py-3 text-ink">{record.location_name}</td>
                      <td className="px-4 py-3 font-mono text-xs text-ink-soft">
                        {record.start_date} → {record.end_date}
                      </td>
                      <td className="px-4 py-3 font-mono text-ink">
                        {record.temperature !== null ? `${record.temperature.toFixed(1)}°C` : "—"}
                      </td>
                      <td className="px-4 py-3 text-ink-soft">{record.weather_condition ?? "—"}</td>
                      <td className="px-4 py-3">
                        <div className="flex justify-end gap-2">
                          <button
                            onClick={() => setEditing(record)}
                            className="rounded-lg p-1.5 text-ink-faint transition hover:bg-surface-muted hover:text-sky"
                            aria-label={`Edit record for ${record.location_name}`}
                          >
                            <Pencil size={15} />
                          </button>
                          <button
                            onClick={() => handleDelete(record.id, record.location_name)}
                            className="rounded-lg p-1.5 text-ink-faint transition hover:bg-rose-soft hover:text-rose"
                            aria-label={`Delete record for ${record.location_name}`}
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {data && data.total > data.page_size && (
          <div className="mt-4 flex items-center justify-between text-sm text-ink-soft">
            <button
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              className="rounded-lg border border-border px-3 py-1.5 disabled:opacity-40"
            >
              Previous
            </button>
            <span>
              Page {data.page} of {Math.ceil(data.total / data.page_size)}
            </span>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={page >= Math.ceil(data.total / data.page_size)}
              className="rounded-lg border border-border px-3 py-1.5 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        )}
      </main>

      {editing && <EditRecordModal record={editing} onClose={() => setEditing(null)} />}
    </div>
  );
}
