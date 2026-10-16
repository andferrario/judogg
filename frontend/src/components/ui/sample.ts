import type { Sample } from "../../api/types";

export function sampleState(sample?: Sample): "small" | "insufficient" | undefined {
  return sample && sample.status !== "ok" ? sample.status : undefined;
}
