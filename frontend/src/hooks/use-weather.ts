"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import * as api from "@/lib/weather-api";
import type { WeatherRecordCreatePayload } from "@/lib/types";

export function useGeocode(query: string, enabled: boolean) {
  return useQuery({
    queryKey: ["geocode", query],
    queryFn: () => api.geocodeLocation(query),
    enabled: enabled && query.trim().length > 0,
    retry: false,
  });
}

export function useCurrentWeather(lat?: number, lon?: number) {
  return useQuery({
    queryKey: ["current-weather", lat, lon],
    queryFn: () => api.getCurrentWeather(lat as number, lon as number),
    enabled: lat !== undefined && lon !== undefined,
  });
}

export function useForecast(lat?: number, lon?: number) {
  return useQuery({
    queryKey: ["forecast", lat, lon],
    queryFn: () => api.getForecast(lat as number, lon as number),
    enabled: lat !== undefined && lon !== undefined,
  });
}

export function useAirQuality(lat?: number, lon?: number) {
  return useQuery({
    queryKey: ["air-quality", lat, lon],
    queryFn: () => api.getAirQuality(lat as number, lon as number),
    enabled: lat !== undefined && lon !== undefined,
  });
}

export function useLocalTime(lat?: number, lon?: number) {
  return useQuery({
    queryKey: ["local-time", lat, lon],
    queryFn: () => api.getLocalTime(lat as number, lon as number),
    enabled: lat !== undefined && lon !== undefined,
  });
}

export function useCountryFlag(countryCode?: string | null) {
  return useQuery({
    queryKey: ["country-flag", countryCode],
    queryFn: () => api.getCountryFlag(countryCode as string),
    enabled: Boolean(countryCode),
  });
}

export function useWeatherHistory(page: number, location?: string) {
  return useQuery({
    queryKey: ["weather-history", page, location],
    queryFn: () => api.listWeatherRecords(page, 10, location),
    placeholderData: (prev) => prev,
  });
}

export function useCreateWeatherRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: WeatherRecordCreatePayload) => api.createWeatherRecord(payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["weather-history"] }),
  });
}

export function useUpdateWeatherRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, changes }: { id: number; changes: Partial<WeatherRecordCreatePayload> }) =>
      api.updateWeatherRecord(id, changes),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["weather-history"] }),
  });
}

export function useDeleteWeatherRecord() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.deleteWeatherRecord(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["weather-history"] }),
  });
}

export function useAskAssistant() {
  return useMutation({
    mutationFn: ({
      question,
      location,
    }: {
      question: string;
      location: { latitude?: number; longitude?: number; location_name?: string };
    }) => api.askAssistant(question, location),
  });
}
