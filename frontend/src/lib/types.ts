export interface WeatherRecord {
  id: number;
  location_name: string;
  latitude: number;
  longitude: number;
  country: string | null;
  start_date: string;
  end_date: string;
  temperature: number | null;
  feels_like: number | null;
  humidity: number | null;
  pressure: number | null;
  wind_speed: number | null;
  visibility: number | null;
  uv_index: number | null;
  weather_condition: string | null;
  created_at: string;
  updated_at: string;
}

export interface PaginatedWeatherRecords {
  total: number;
  page: number;
  page_size: number;
  items: WeatherRecord[];
}

export interface WeatherRecordCreatePayload {
  location_name: string;
  latitude: number;
  longitude: number;
  start_date: string;
  end_date: string;
  country?: string | null;
  temperature?: number | null;
  humidity?: number | null;
  weather_condition?: string | null;
}

export interface GeocodeResult {
  name: string;
  latitude: number;
  longitude: number;
  country: string | null;
}

export interface CurrentWeather {
  temperature: number;
  feels_like: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  visibility: number;
  uv_index: number | null;
  weather_condition: string;
  description: string;
  icon: string;
  sunrise: number | null;
  sunset: number | null;
  timezone_offset: number | string | null;
}

export interface ForecastDay {
  date: string;
  temp_min: number;
  temp_max: number;
  humidity: number;
  wind_speed: number;
  weather_condition: string;
  description: string;
  icon: string;
  pop: number;
}

export interface AssistantResponse {
  answer: string;
  recommendation: "favorable" | "caution" | "unfavorable";
  reasoning: string[];
  source: string;
}

export interface AirQuality {
  aqi: number | null;
  label: string;
}

export interface TimezoneInfo {
  datetime: string;
  timezone: string;
  utc_offset?: unknown;
  note?: string;
}

export interface CountryFlag {
  country_code: string;
  flag_url: string;
  flag_svg_url: string;
}

export interface ApiErrorShape {
  error: string;
  message: string;
  details?: Record<string, unknown>;
}
