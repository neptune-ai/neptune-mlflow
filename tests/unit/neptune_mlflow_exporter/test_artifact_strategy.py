from unittest.mock import (
    MagicMock,
    patch,
)

from mlflow.entities import FileInfo

from neptune_mlflow_exporter.impl.artifact_strategy import (
    DirectoryUploadStrategy,
    FileUploadStrategy,
)


@patch("neptune_mlflow_exporter.impl.artifact_strategy.download_artifacts")
def test_file_upload_strategy_does_not_upload_file_above_limit_size(mock_download_artifacts):
    strategy = FileUploadStrategy(tracking_uri="", max_file_size=500)
    file_info = FileInfo("some_path", False, 1000)

    strategy.upload_artifact(MagicMock(), file_info, MagicMock())

    mock_download_artifacts.assert_not_called()


@patch("neptune.handler.Handler.upload_files")
@patch("neptune_mlflow_exporter.impl.artifact_strategy.download_artifacts")
@patch("neptune_mlflow_exporter.impl.artifact_strategy.get_dir_size", return_value=1000)
def test_directory_upload_strategy_does_not_upload_dir_above_limit_size(
    mock_get_dir_size, mock_download_artifacts, mock_upload
):
    strategy = DirectoryUploadStrategy(tracking_uri="", max_file_size=500)
    file_info = FileInfo("some_path", True, None)

    strategy.upload_artifact(MagicMock(), file_info, MagicMock())

    # size estimated after dir is downloaded
    mock_download_artifacts.assert_called_once()
    mock_get_dir_size.assert_called_once()

    mock_upload.assert_not_called()
