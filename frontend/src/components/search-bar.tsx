"use client";

import { useState } from "react";
import { LocateFixed, Search, Loader2 } from "lucide-react";
import { cn } from "@/lib/cn";

interface SearchBarProps {
  onSearch: (query: string) => void;
  onUseCurrentLocation: (lat: number, lon: number) => void;
  isLoading?: boolean;
}

export function SearchBar({ onSearch, onUseCurrentLocation, isLoading }: SearchBarProps) {
  const [value, setValue] = useState("");
  const [locating, setLocating] = useState(false);
  const [geoError, setGeoError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) onSearch(value.trim());
  };

  const handleUseLocation = () => {
    setGeoError(null);
    if (!navigator.geolocation) {
      setGeoError("Geolocation isn't supported by this browser.");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocating(false);
        onUseCurrentLocation(position.coords.latitude, position.coords.longitude);
      },
      (err) => {
        setLocating(false);
        setGeoError(
          err.code === err.PERMISSION_DENIED
            ? "Location access was denied. Search by city or zip instead."
            : "Couldn't determine your location. Try searching instead."
        );
      },
      { timeout: 10_000 }
    );
  };

  return (
    <div className="w-full">
      <form onSubmit={handleSubmit} className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search
            size={18}
            className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint"
          />
          <input
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="City, zip/postal code, or coordinates (e.g. 40.71,-74.00)"
            className={cn(
              "w-full rounded-xl border border-border bg-surface py-3 pl-10 pr-4 text-sm",
              "text-ink placeholder:text-ink-faint",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sky/40"
            )}
            aria-label="Search for a location"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="rounded-xl bg-sky px-4 py-3 text-sm font-medium text-white transition hover:opacity-90 disabled:opacity-50"
        >
          {isLoading ? <Loader2 size={16} className="animate-spin" /> : "Search"}
        </button>
        <button
          type="button"
          onClick={handleUseLocation}
          disabled={locating}
          title="Use my current location"
          className="flex items-center gap-1.5 rounded-xl border border-border bg-surface px-3 py-3 text-sm text-ink-soft transition hover:text-sky disabled:opacity-50"
        >
          {locating ? <Loader2 size={16} className="animate-spin" /> : <LocateFixed size={16} />}
          <span className="hidden sm:inline">Near me</span>
        </button>
      </form>
      {geoError && <p className="mt-2 text-xs text-rose">{geoError}</p>}
    </div>
  );
}
