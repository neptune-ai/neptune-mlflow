from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

from mlflow.entities import FileInfo

from neptune_mlflow_exporter.impl.artifact_strategy import (
    DirectoryUploadStrategy,
    FileUploadStrategy,
)


@patch("neptune_mlflow_exporter.impl.artifact_strategy.ArtifactUploadStrategy._download_artifacts")
def test_file_upload_strategy_does_nothing_for_dir(mock_download_artifacts):
    strategy = FileUploadStrategy(tracking_uri="", max_file_size=5000)
    file_info = FileInfo("some_path", True, None)
    neptune_run = Mock()

    strategy.upload_artifact(neptune_run, file_info, "some_id")

    neptune_run.assert_not_called()
    mock_download_artifacts.assert_not_called()


@patch("neptune_mlflow_exporter.impl.artifact_strategy.ArtifactUploadStrategy._download_artifacts")
def test_file_upload_strategy_does_not_upload_file_above_limit_size(mock_download_artifacts):
    strategy = FileUploadStrategy(tracking_uri="", max_file_size=500)
    file_info = FileInfo("some_path", False, 1000)
    neptune_run = Mock()

    strategy.upload_artifact(neptune_run, file_info, "some_id")

    neptune_run.assert_not_called()
    mock_download_artifacts.assert_not_called()


@patch("neptune_mlflow_exporter.impl.artifact_strategy.ArtifactUploadStrategy._download_artifacts")
def test_directory_upload_strategy_does_nothing_for_file(mock_download_artifacts):
    strategy = DirectoryUploadStrategy(tracking_uri="", max_file_size=5000)
    file_info = FileInfo("some_path", False, 100)
    neptune_run = Mock()

    strategy.upload_artifact(neptune_run, file_info, "some_id")

    neptune_run.assert_not_called()
    mock_download_artifacts.assert_not_called()


@patch("neptune_mlflow_exporter.impl.artifact_strategy.ArtifactUploadStrategy._download_artifacts")
@patch("neptune_mlflow_exporter.impl.artifact_strategy.get_dir_size", return_value=1000)
def test_directory_upload_strategy_does_not_upload_dir_above_limit_size(mock_get_dir_size, mock_download_artifacts):
    strategy = DirectoryUploadStrategy(tracking_uri="", max_file_size=500)
    file_info = FileInfo("some_path", True, None)
    neptune_run = MagicMock()

    strategy.upload_artifact(neptune_run, file_info, "some_id")

    # size estimated after dir is downloaded
    mock_download_artifacts.assert_called_once()
    mock_get_dir_size.assert_called_once()

    # above size limit => no upload to Neptune
    neptune_run.assert_not_called()
