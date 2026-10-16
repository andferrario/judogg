from pathlib import Path

from pydantic_settings import BaseSettings


class IngestionSettings(BaseSettings):
    database_url: str
    seeds_dir: Path = Path("seeds")
    fetch_delay_s: float = 1.0
    fetch_timeout_s: float = 30.0
    fetch_retries: int = 2
