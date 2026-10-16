import createClient from "openapi-fetch";
import type { paths } from "./schema";
import type { ErrorBody, ErrorDetail } from "./types";

export class ApiError extends Error {
  readonly status: number;
  readonly code: ErrorDetail["code"];
  readonly field: string | null;

  constructor(status: number, detail: ErrorDetail) {
    super(detail.message);
    this.name = "ApiError";
    this.status = status;
    this.code = detail.code;
    this.field = detail.field;
  }
}

export const api = createClient<paths>({
  // An absolute base URL: the fetch of Node, used by the tests, rejects relative URLs.
  baseUrl: window.location.origin,
  // Looked up on every call: the test server replaces the global fetch after this module is loaded.
  fetch: (request) => globalThis.fetch(request),
});

type Result<T> = { data?: T; error?: unknown; response: Response };

export async function unwrap<T>(request: Promise<Result<T>>): Promise<T> {
  const { data, error, response } = await request;
  if (data !== undefined) return data;
  if (isErrorBody(error)) throw new ApiError(response.status, error.error);
  throw new Error(`The API answered ${response.status}`);
}

function isErrorBody(value: unknown): value is ErrorBody {
  return typeof value === "object" && value !== null && "error" in value;
}
