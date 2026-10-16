from pathlib import Path

from pydantic_settings import BaseSettings

from judogg.app.domain.model import Thresholds


class AppSettings(BaseSettings):
    database_url: str
    seeds_dir: Path = Path("seeds")
    sample_ok: int = 20
    sample_small: int = 5
    athlete_sample_ok: int = 10
    athlete_sample_small: int = 5
    specialist_share: float = 0.4
    min_scores_country: int = 30
    unknown_technique_warning: float = 0.1

    def thresholds(self) -> Thresholds:
        return Thresholds(
            self.sample_ok,
            self.sample_small,
            self.athlete_sample_ok,
            self.athlete_sample_small,
            self.specialist_share,
            self.min_scores_country,
            self.unknown_technique_warning,
        )
