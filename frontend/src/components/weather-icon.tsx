"use client";

import {
  Cloud,
  CloudDrizzle,
  CloudFog,
  CloudLightning,
  CloudRain,
  CloudSnow,
  CloudSun,
  Sun,
  Moon,
  Wind,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";

const ICON_MAP: Record<string, LucideIcon> = {
  "01d": Sun,
  "01n": Moon,
  "02d": CloudSun,
  "02n": Cloud,
  "03d": Cloud,
  "03n": Cloud,
  "04d": Cloud,
  "04n": Cloud,
  "09d": CloudDrizzle,
  "09n": CloudDrizzle,
  "10d": CloudRain,
  "10n": CloudRain,
  "11d": CloudLightning,
  "11n": CloudLightning,
  "13d": CloudSnow,
  "13n": CloudSnow,
  "50d": CloudFog,
  "50n": CloudFog,
};

const CONDITION_FALLBACK: Record<string, LucideIcon> = {
  clear: Sun,
  clouds: Cloud,
  rain: CloudRain,
  drizzle: CloudDrizzle,
  thunderstorm: CloudLightning,
  snow: CloudSnow,
  mist: CloudFog,
  fog: CloudFog,
  haze: CloudFog,
  wind: Wind,
};

export function WeatherIcon({
  icon,
  condition,
  className,
  size = 40,
}: {
  icon?: string | null;
  condition?: string | null;
  className?: string;
  size?: number;
}) {
  const IconComponent =
    (icon && ICON_MAP[icon]) ||
    (condition && CONDITION_FALLBACK[condition.toLowerCase()]) ||
    Cloud;

  return (
    <IconComponent
      size={size}
      strokeWidth={1.6}
      className={cn("text-sky", className)}
      aria-hidden="true"
    />
  );
}
