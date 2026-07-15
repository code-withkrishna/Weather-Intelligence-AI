"use client";

import dynamic from "next/dynamic";
import { MapPin } from "lucide-react";

const MapPanelInner = dynamic(() => import("@/components/map-panel-inner"), {
  ssr: false,
  loading: () => (
    <div className="flex h-64 w-full items-center justify-center rounded-2xl bg-surface-muted text-ink-faint">
      <MapPin size={20} className="animate-pulse" />
    </div>
  ),
});

export function MapPanel({
  lat,
  lon,
  locationName,
}: {
  lat: number;
  lon: number;
  locationName: string;
}) {
  return (
    <div className="overflow-hidden rounded-2xl border border-border bg-surface p-2 shadow-[var(--shadow-card)]">
      <MapPanelInner lat={lat} lon={lon} locationName={locationName} />
    </div>
  );
}
