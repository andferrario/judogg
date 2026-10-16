import os
from collections.abc import Iterator

import pytest
from sqlalchemy import Engine, create_engine


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    test_engine = create_engine(os.environ["TEST_DATABASE_URL"])
    yield test_engine
    test_engine.dispose()
