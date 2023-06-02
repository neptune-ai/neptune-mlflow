__all__ = [
    "ArtifactUploadStrategy",
    "FileUploadStrategy",
    "DirectoryUploadStrategy",
]

import os
import shutil
from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path

from mlflow.artifacts import download_artifacts
from mlflow.entities import FileInfo

try:
    from neptune import Run
except ImportError:
    from neptune.new.metadata_containers import Run


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

    def _download_artifacts(self, run_id: str, path: str) -> str:
        return download_artifacts(run_id=run_id, artifact_path=path, dst_path=".", tracking_uri=self._uri)

    @abstractmethod
    def upload_artifact(self, neptune_run: Run, info: FileInfo, run_id: str) -> None:
        ...


class FileUploadStrategy(ArtifactUploadStrategy):
    def upload_artifact(self, neptune_run: Run, info: FileInfo, run_id: str) -> None:
        if info.is_dir or info.file_size > self._max_size:
            return

        local_path = None
        try:
            local_path = self._download_artifacts(run_id=run_id, path=info.path)
            local_path = Path(local_path).name
            neptune_run[f"{self.BASE_NAMESPACE}/{local_path}"].upload(local_path)
            neptune_run.wait()

        finally:
            if local_path and os.path.isfile(local_path):
                os.remove(local_path)


class DirectoryUploadStrategy(ArtifactUploadStrategy):
    def get_dir_size(self, path: str):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.get_dir_size(entry.path)
        return total

    def upload_artifact(self, neptune_run: Run, info: FileInfo, run_id: str) -> None:
        if not info.is_dir:
            return

        # download directory first and then check the size
        local_path = None
        try:
            local_path = self._download_artifacts(run_id=run_id, path=info.path)

            dir_size = self.get_dir_size(local_path)
            if dir_size > self._max_size:
                return
            local_path = Path(local_path)
            neptune_run[f"{self.BASE_NAMESPACE}/{local_path.name}"].upload_files(str(local_path / "*"))
            neptune_run.wait()

        finally:
            if local_path and os.path.isdir(local_path):
                shutil.rmtree(local_path)
