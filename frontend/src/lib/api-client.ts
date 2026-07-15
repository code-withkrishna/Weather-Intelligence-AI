import axios, { AxiosError } from "axios";
import type { ApiErrorShape } from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
});

/**
 * A normalized, user-safe error every API call rejects with.
 * Centralizing this here means every hook/component gets consistent,
 * human-readable messages without repeating try/catch parsing logic.
 */
export class ApiError extends Error {
  code: string;
  status?: number;

  constructor(message: string, code: string, status?: number) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorShape>) => {
    if (error.response) {
      const body = error.response.data;
      throw new ApiError(
        body?.message ?? "Something went wrong talking to the server.",
        body?.error ?? "unknown_error",
        error.response.status
      );
    }
    if (error.request) {
      throw new ApiError(
        "Couldn't reach the weather server. Check your connection and try again.",
        "network_error"
      );
    }
    throw new ApiError(error.message || "Unexpected error.", "unknown_error");
  }
);
