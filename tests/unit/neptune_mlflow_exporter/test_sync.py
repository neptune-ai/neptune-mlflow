import pytest

from neptune_mlflow_exporter.impl.sync import sync


def test_invalid_max_artifact_size() -> None:
    with pytest.raises(ValueError):
        sync(max_artifact_size=0)

    with pytest.raises(ValueError):
        sync(max_artifact_size=-100)

    with pytest.raises(TypeError):
        sync(max_artifact_size=50.5)
