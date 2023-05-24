import os
from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path

from mlflow.artifacts import download_artifacts
from mlflow.entities import FileInfo
from neptune import Run


class ArtifactUploadStrategy(ABC):
    BASE_NAMESPACE = "artifacts"

    def __init__(
        self,
        *,
        tracking_uri: str,
        max_file_size: int,
    ):

        self._uri = tracking_uri
        self._max_size = max_file_size

    @abstractmethod
    def upload_artifact(self, neptune_run: Run, info: FileInfo, run_id: str) -> None:
        ...


class FileUploadStrategy(ArtifactUploadStrategy):
    def upload_artifact(self, neptune_run: Run, info: FileInfo, run_id: str) -> None:
        if info.file_size > self._max_size:
            return

        local_path = ""
        try:
            local_path = download_artifacts(
                run_id=run_id, artifact_path=info.path, dst_path=".", tracking_uri=self._uri
            )
            local_path = Path(local_path).name
            neptune_run[f"{self.BASE_NAMESPACE}/{local_path}"].upload(local_path)
            neptune_run.wait()

        finally:
            if local_path:
                os.remove(local_path)


class DirectoryUploadStrategy(ArtifactUploadStrategy):
    def upload_artifact(self, neptune_run: Run, info: FileInfo, run_id: str) -> None:
        ...
