try:
    from neptune import (
        Project,
        init_project,
    )
except ImportError:
    from neptune.new import init_project
    from neptune.new.metadata_containers import Project

import pytest

from neptune_mlflow import NeptuneExporter


@pytest.fixture(scope="session")
def neptune_project() -> Project:
    with init_project(mode="debug", project="organization/project") as project:
        yield project


@pytest.fixture(scope="session")
def neptune_exporter(neptune_project) -> NeptuneExporter:
    yield NeptuneExporter(project=neptune_project, mlflow_tracking_uri="test_tracking_uri")
