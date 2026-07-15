"use client";

import Image from "next/image";
import { Clock, Wind as AqiIcon } from "lucide-react";
import { useAirQuality, useCountryFlag, useLocalTime } from "@/hooks/use-weather";

const AQI_COLORS: Record<number, string> = {
  1: "text-teal",
  2: "text-teal",
  3: "text-amber",
  4: "text-rose",
  5: "text-rose",
};

export function InfoBadges({
  lat,
  lon,
  countryCode,
}: {
  lat?: number;
  lon?: number;
  countryCode?: string | null;
}) {
  const { data: aqi } = useAirQuality(lat, lon);
  const { data: time } = useLocalTime(lat, lon);
  const { data: flag } = useCountryFlag(countryCode);

  return (
    <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
      <div className="flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3">
        <AqiIcon size={18} className={aqi?.aqi ? AQI_COLORS[aqi.aqi] : "text-ink-faint"} />
        <div>
          <p className="text-xs text-ink-faint">Air Quality</p>
          <p className="text-sm font-medium text-ink">{aqi?.label ?? "—"}</p>
        </div>
      </div>

      <div className="flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3">
        <Clock size={18} className="text-ink-faint" />
        <div>
          <p className="text-xs text-ink-faint">Local Time</p>
          <p className="font-mono text-sm font-medium text-ink">
            {time?.datetime
              ? new Date(time.datetime).toLocaleTimeString(undefined, {
                  hour: "numeric",
                  minute: "2-digit",
                })
              : "—"}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3 rounded-xl border border-border bg-surface px-4 py-3">
        {flag?.flag_url ? (
          <Image
            src={flag.flag_url}
            alt={`${flag.country_code} flag`}
            width={28}
            height={20}
            className="rounded-sm object-cover"
            unoptimized
          />
        ) : (
          <div className="h-5 w-7 rounded-sm bg-surface-muted" />
        )}
        <div>
          <p className="text-xs text-ink-faint">Country</p>
          <p className="text-sm font-medium text-ink">{flag?.country_code ?? "—"}</p>
        </div>
      </div>
    </div>
  );
}
