import { http, HttpResponse } from "msw";
import { setupServer } from "msw/node";
import {
  athlete,
  athleteAllWeights,
  counters,
  meta,
  outcomes,
  overview,
  pairs,
  penalties,
  repertoire,
  repertoireSeoiNage,
  repertoireWith,
  scoresPage1,
  scoresPage2,
  seoiNageDetail,
  tierList,
  uchiMataDetail,
  unknownAthlete,
  unknownTechnique,
  weightMatrix,
  yokoShihoGatameDetail,
} from "./fixtures";

const DETAILS: Record<string, unknown> = {
  uchi_mata: uchiMataDetail,
  seoi_nage: seoiNageDetail,
  yoko_shiho_gatame: yokoShihoGatameDetail,
};

// The more specific technique paths come first: "/api/techniques/:code" would also match "by-weight".
export const server = setupServer(
  http.get("/api/meta", () => HttpResponse.json(meta)),
  http.get("/api/overview", () => HttpResponse.json(overview)),
  http.get("/api/athletes", () => HttpResponse.json({ rows: [] })),
  http.get("/api/techniques/by-weight", () => HttpResponse.json(weightMatrix)),
  http.get("/api/techniques/:code/scores", ({ request }) =>
    HttpResponse.json(new URL(request.url).searchParams.get("page") === "2" ? scoresPage2 : scoresPage1),
  ),
  http.get("/api/techniques/:code", ({ params }) => {
    const detail = DETAILS[String(params.code)];
    return detail ? HttpResponse.json(detail) : HttpResponse.json(unknownTechnique, { status: 404 });
  }),
  http.get("/api/techniques", () => HttpResponse.json(tierList)),
  http.get("/api/outcomes", () => HttpResponse.json(outcomes)),
  http.get("/api/repertoire/pairs", () => HttpResponse.json(pairs)),
  http.get("/api/repertoire", ({ request }) => {
    const query = new URL(request.url).searchParams;
    if (query.get("with")) return HttpResponse.json(repertoireWith);
    return HttpResponse.json(query.get("technique") === "seoi_nage" ? repertoireSeoiNage : repertoire);
  }),
  http.get("/api/penalties", () => HttpResponse.json(penalties)),
  http.get("/api/athletes/:id", ({ params, request }) => {
    if (params.id !== "900323") return HttpResponse.json(unknownAthlete, { status: 404 });
    const scope = new URL(request.url).searchParams.get("similar_scope");
    return HttpResponse.json(scope === "all" ? athleteAllWeights : athlete);
  }),
  http.get("/api/counters", () => HttpResponse.json(counters)),
);
