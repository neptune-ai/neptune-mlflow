from unittest.mock import patch

import pytest

from neptune_mlflow_exporter.impl.sync import sync


def test_invalid_max_artifact_size() -> None:
    with pytest.raises(ValueError):
        sync(max_artifact_size=0)

    with pytest.raises(ValueError):
        sync(max_artifact_size=-100)

    with pytest.raises(TypeError):
        sync(max_artifact_size=50.5)


@patch("neptune.init_project")
@patch("mlflow.tracking.MlflowClient")
def test_init_project_and_mlflow_client_called_once(mock_client, mock_init_project) -> None:
    sync()
    mock_init_project.assert_called_once_with()
    mock_client.assert_called_once_with()
