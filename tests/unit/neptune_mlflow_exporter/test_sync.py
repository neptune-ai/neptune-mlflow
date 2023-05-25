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


def test_init_project_called_once() -> None:
    with patch("neptune.init_project") as mock_init_project:
        sync()
        mock_init_project.assert_called_once_with()
