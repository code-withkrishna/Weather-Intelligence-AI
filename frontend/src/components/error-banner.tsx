"use client";

import { AlertTriangle, WifiOff, MapPinOff, ServerCrash } from "lucide-react";
import { ApiError } from "@/lib/api-client";

const ICONS: Record<string, React.ComponentType<{ size?: number; className?: string }>> = {
  network_error: WifiOff,
  location_not_found: MapPinOff,
  external_api_unavailable: ServerCrash,
  external_api_error: ServerCrash,
};

export function ErrorBanner({ error }: { error: unknown }) {
  if (!error) return null;

  const isApiError = error instanceof ApiError;
  const code = isApiError ? error.code : "unknown_error";
  const message = isApiError
    ? error.message
    : "Something unexpected happened. Please try again.";
  const Icon = ICONS[code] ?? AlertTriangle;

  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-xl border border-rose/30 bg-rose-soft px-4 py-3 text-sm text-rose"
    >
      <Icon size={18} className="mt-0.5 shrink-0" />
      <div>
        <p className="font-medium">
          {code === "location_not_found"
            ? "Location not found"
            : code === "network_error"
            ? "Connection problem"
            : code === "external_api_unavailable"
            ? "Weather service unavailable"
            : "Something went wrong"}
        </p>
        <p className="mt-0.5 text-rose/90">{message}</p>
      </div>
    </div>
  );
}
