import type { components } from "./schema";

type Schemas = components["schemas"];

export type Meta = Schemas["Meta"];
export type ApiFilters = Schemas["Filters"];
export type Defaults = Schemas["Defaults"];
export type Sample = Schemas["Sample"];
export type WarningItem = Schemas["WarningItem"];
export type ErrorDetail = Schemas["ErrorDetail"];
export type ErrorBody = Schemas["ErrorBody"];
export type WeightOption = Schemas["WeightOption"];
export type WeightRef = Schemas["WeightRef"];
export type Athlete = Schemas["Athlete"];
export type SearchRow = Schemas["SearchRow"];
export type AthleteSearch = Schemas["AthleteSearch"];
export type OverviewResponse = Schemas["Envelope_Overview_"];

export type TechniqueRef = Schemas["TechniqueRef"];
export type ValueCounts = Schemas["ValueCounts"];
export type SideCounts = Schemas["SideCounts"];
export type TimingBin = Schemas["TimingBin"];
export type TrendPoint = Schemas["TrendPoint"];

export type TierListResponse = Schemas["Envelope_TierList_"];
export type TierRow = Schemas["TierRow"];
export type WeightMatrixResponse = Schemas["Envelope_WeightMatrix_"];
export type OutcomesResponse = Schemas["Envelope_OutcomeTable_"];
export type OutcomeRow = Schemas["WeightOutcomes"];
export type TotalOutcomes = Schemas["OutcomesWithShido"];
export type TechniqueDetailResponse = Schemas["Envelope_TechniqueDetail_"];
export type TechniqueScoresResponse = Schemas["Envelope_TechniqueScores_"];
export type RepertoireResponse = Schemas["Envelope_Repertoire_"];
export type CountersResponse = Schemas["Envelope_Counters_"];

export type RepertoirePairsResponse = Schemas["Envelope_RepertoirePairs_"];
export type PenaltiesResponse = Schemas["Envelope_Penalties_"];
export type AthleteResponse = Schemas["AthleteResponse"];
export type AthleteDetail = Schemas["AthleteDetail"];
export type PenaltyBin = Schemas["PenaltyBin"];
export type Similar = Schemas["Similar"];
