import { http, HttpResponse } from "msw";
import { invalidWeightError } from "../test/fixtures";
import { server } from "../test/server";
import { api, ApiError, unwrap } from "./client";

test("returns the body of a successful response", async () => {
  const meta = await unwrap(api.GET("/api/meta"));
  expect(meta.defaults.ruleset).toEqual([2017, 2018, 2025]);
});

test("turns the API error format into an ApiError", async () => {
  server.use(http.get("/api/overview", () => HttpResponse.json(invalidWeightError, { status: 400 })));
  const error = await unwrap(api.GET("/api/overview", { params: { query: { gender: "f", weight: "m-73" } } })).catch(
    (caught: unknown) => caught,
  );
  expect(error).toBeInstanceOf(ApiError);
  expect(error).toMatchObject({
    status: 400,
    code: "invalid_parameter",
    field: "weight",
    message: "weight category m-73 does not match gender f",
  });
});

test("any other failure is a plain Error with the status", async () => {
  server.use(http.get("/api/overview", () => new HttpResponse("Internal Server Error", { status: 500 })));
  const error = await unwrap(api.GET("/api/overview")).catch((caught: unknown) => caught);
  expect(error).not.toBeInstanceOf(ApiError);
  expect(error).toEqual(new Error("The API answered 500"));
});
