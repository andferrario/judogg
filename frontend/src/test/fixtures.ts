import type {
  AthleteResponse,
  AthleteSearch,
  CountersResponse,
  ErrorBody,
  Meta,
  OutcomesResponse,
  OverviewResponse,
  PenaltiesResponse,
  RepertoirePairsResponse,
  RepertoireResponse,
  TechniqueDetailResponse,
  TechniqueScoresResponse,
  TierListResponse,
  WeightMatrixResponse,
} from "../api/types";
import athletesJson from "./fixtures/athletes_search.json";
import errorJson from "./fixtures/error_weight_gender.json";
import metaJson from "./fixtures/meta.json";
import overviewJson from "./fixtures/overview.json";
import countersJson from "./fixtures/counters.json";
import outcomesJson from "./fixtures/outcomes.json";
import repertoireJson from "./fixtures/repertoire.json";
import scoresPage1Json from "./fixtures/scores_page_1.json";
import scoresPage2Json from "./fixtures/scores_page_2.json";
import noScoresJson from "./fixtures/technique_no_scores.json";
import seoiNageJson from "./fixtures/technique_seoi_nage.json";
import uchiMataJson from "./fixtures/technique_uchi_mata.json";
import unknownTechniqueJson from "./fixtures/technique_unknown.json";
import yokoShihoGatameJson from "./fixtures/technique_yoko_shiho_gatame.json";
import tierListJson from "./fixtures/tier_list.json";
import tierListByAthleteJson from "./fixtures/tier_list_by_athlete.json";
import weightMatrixJson from "./fixtures/weight_matrix.json";
import athleteAllWeightsJson from "./fixtures/athlete_all_weights.json";
import athleteJson from "./fixtures/athlete.json";
import athleteUnknownJson from "./fixtures/athlete_unknown.json";
import pairsJson from "./fixtures/pairs.json";
import pairsNoneJson from "./fixtures/pairs_none.json";
import penaltiesJson from "./fixtures/penalties.json";
import repertoireSeoiNageJson from "./fixtures/repertoire_seoi_nage.json";
import repertoireWithJson from "./fixtures/repertoire_with.json";

// Real responses of the backend (its golden files): JSON imports type enums as plain strings.
export const meta = metaJson as Meta;
export const overview = overviewJson as OverviewResponse;
export const invalidWeightError = errorJson as ErrorBody;
export const athleteSearch = athletesJson as AthleteSearch;
export const tierList = tierListJson as TierListResponse;
export const tierListByAthlete = tierListByAthleteJson as TierListResponse;
export const weightMatrix = weightMatrixJson as WeightMatrixResponse;
export const outcomes = outcomesJson as OutcomesResponse;
export const uchiMataDetail = uchiMataJson as TechniqueDetailResponse;
export const seoiNageDetail = seoiNageJson as TechniqueDetailResponse;
export const yokoShihoGatameDetail = yokoShihoGatameJson as TechniqueDetailResponse;
export const noScoresDetail = noScoresJson as TechniqueDetailResponse;
export const unknownTechnique = unknownTechniqueJson as ErrorBody;
export const scoresPage1 = scoresPage1Json as TechniqueScoresResponse;
export const scoresPage2 = scoresPage2Json as TechniqueScoresResponse;
export const repertoire = repertoireJson as RepertoireResponse;
export const counters = countersJson as CountersResponse;
export const pairs = pairsJson as RepertoirePairsResponse;
export const pairsNone = pairsNoneJson as RepertoirePairsResponse;
export const repertoireWith = repertoireWithJson as RepertoireResponse;
export const repertoireSeoiNage = repertoireSeoiNageJson as RepertoireResponse;
export const penalties = penaltiesJson as PenaltiesResponse;
export const athlete = athleteJson as AthleteResponse;
export const athleteAllWeights = athleteAllWeightsJson as AthleteResponse;
export const unknownAthlete = athleteUnknownJson as ErrorBody;
