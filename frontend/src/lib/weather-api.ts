import { apiClient } from "./api-client";
import type {
  AirQuality,
  AssistantResponse,
  CountryFlag,
  CurrentWeather,
  ForecastDay,
  GeocodeResult,
  PaginatedWeatherRecords,
  TimezoneInfo,
  WeatherRecord,
  WeatherRecordCreatePayload,
} from "./types";

// --- Live lookups (not persisted) ------------------------------------------
export const geocodeLocation = async (query: string): Promise<GeocodeResult> => {
  const { data } = await apiClient.get("/live/geocode", { params: { q: query } });
  return data;
};

export const getCurrentWeather = async (lat: number, lon: number): Promise<CurrentWeather> => {
  const { data } = await apiClient.get("/live/current", { params: { lat, lon } });
  return data;
};

export const getForecast = async (lat: number, lon: number): Promise<ForecastDay[]> => {
  const { data } = await apiClient.get("/live/forecast", { params: { lat, lon } });
  return data;
};

// --- Extras -----------------------------------------------------------------
export const getAirQuality = async (lat: number, lon: number): Promise<AirQuality> => {
  const { data } = await apiClient.get("/extras/air-quality", { params: { lat, lon } });
  return data;
};

export const getLocalTime = async (lat: number, lon: number): Promise<TimezoneInfo> => {
  const { data } = await apiClient.get("/extras/timezone", { params: { lat, lon } });
  return data;
};

export const getCountryFlag = async (countryCode: string): Promise<CountryFlag> => {
  const { data } = await apiClient.get("/extras/country-flag", {
    params: { country_code: countryCode },
  });
  return data;
};

// --- AI Assistant -------------------------------------------------------------
export const askAssistant = async (
  question: string,
  location: { latitude?: number; longitude?: number; location_name?: string }
): Promise<AssistantResponse> => {
  const { data } = await apiClient.post("/assistant/ask", { question, ...location });
  return data;
};

// --- CRUD: persisted weather history ------------------------------------------
export const createWeatherRecord = async (
  payload: WeatherRecordCreatePayload
): Promise<WeatherRecord> => {
  const { data } = await apiClient.post("/weather", payload);
  return data;
};

export const listWeatherRecords = async (
  page = 1,
  pageSize = 20,
  location?: string
): Promise<PaginatedWeatherRecords> => {
  const { data } = await apiClient.get("/weather", {
    params: { page, page_size: pageSize, location },
  });
  return data;
};

export const getWeatherRecord = async (id: number): Promise<WeatherRecord> => {
  const { data } = await apiClient.get(`/weather/${id}`);
  return data;
};

export const updateWeatherRecord = async (
  id: number,
  changes: Partial<WeatherRecordCreatePayload>
): Promise<WeatherRecord> => {
  const { data } = await apiClient.put(`/weather/${id}`, changes);
  return data;
};

export const deleteWeatherRecord = async (id: number): Promise<void> => {
  await apiClient.delete(`/weather/${id}`);
};

export const exportUrl = (format: "csv" | "json" | "pdf", location?: string): string => {
  const params = new URLSearchParams({ format });
  if (location) params.set("location", location);
  return `${apiClient.defaults.baseURL}/weather/export?${params.toString()}`;
};
