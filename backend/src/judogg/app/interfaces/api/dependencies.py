from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import create_engine

from judogg.app.application.ports import DatasetReader
from judogg.app.domain.meta import GlossaryEntry
from judogg.app.domain.model import DEFAULT_MIN_SCORES_TECHNIQUE, Thresholds
from judogg.app.infrastructure.glossary import load_glossary
from judogg.app.infrastructure.reader import PostgresDatasetReader
from judogg.app.infrastructure.settings import AppSettings


@dataclass(frozen=True)
class Services:
    reader: DatasetReader
    thresholds: Thresholds
    glossary: tuple[GlossaryEntry, ...]


def build_services() -> Services:
    """Composition root: the only place that instantiates infrastructure classes."""
    settings = AppSettings()
    thresholds = settings.thresholds()
    glossary = load_glossary(
        settings.seeds_dir / "glossary.yaml", DEFAULT_MIN_SCORES_TECHNIQUE, thresholds.specialist_share
    )
    return Services(PostgresDatasetReader(create_engine(settings.database_url)), thresholds, glossary)


def get_services(request: Request) -> Services:
    state = request.app.state
    if state.services is None:
        state.services = state.services_factory()
    services: Services = state.services
    return services


ServicesDep = Annotated[Services, Depends(get_services)]
