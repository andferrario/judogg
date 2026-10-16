import { ApiError } from "./client";
import { createQueryClient } from "./queryClient";

test("answers of the API are not retried, other failures twice", () => {
  const retry = createQueryClient().getDefaultOptions().queries?.retry as (failures: number, error: Error) => boolean;
  expect(retry(0, new ApiError(400, { code: "invalid_parameter", message: "bad", field: "gender" }))).toBe(false);
  expect(retry(0, new Error("The API answered 500"))).toBe(true);
  expect(retry(1, new Error("The API answered 500"))).toBe(true);
  expect(retry(2, new Error("The API answered 500"))).toBe(false);
});
