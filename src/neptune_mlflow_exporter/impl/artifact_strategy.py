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
from typing import TYPE_CHECKING

from mlflow.artifacts import download_artifacts
from mlflow.entities import FileInfo

if TYPE_CHECKING:
    try:
        from neptune import Run
    except ImportError:
        from neptune.new.metadata_containers import Run


class ArtifactUploadStrategy(ABC):
    BASE_NAMESPACE = "artifacts"
    TEMP_DIR = "./temp"

    def __init__(
        self,
        *,
        tracking_uri: str,
        max_file_size: int,
    ):

        self._uri = tracking_uri
        self._max_size = max_file_size

    def _download_artifacts(self, run_id: str, path: str) -> None:
        if not os.path.isdir(self.TEMP_DIR):
            os.mkdir(self.TEMP_DIR)

        download_artifacts(run_id=run_id, artifact_path=path, dst_path=self.TEMP_DIR, tracking_uri=self._uri)

    def _is_size_ok(self, info: FileInfo, run_id: str) -> bool:
        if not info.is_dir:
            return info.file_size <= self._max_size

        self._download_artifacts(run_id=run_id, path=info.path)

        dir_size = get_dir_size(self.TEMP_DIR)

        return dir_size <= self._max_size

    def _clean_up(self) -> None:
        if os.path.isdir(self.TEMP_DIR):
            shutil.rmtree(self.TEMP_DIR)

    @abstractmethod
    def upload_artifact(self, neptune_run: "Run", info: FileInfo, run_id: str) -> None:
        ...


class FileUploadStrategy(ArtifactUploadStrategy):
    def upload_artifact(self, neptune_run: "Run", info: FileInfo, run_id: str) -> None:
        if info.is_dir or not self._is_size_ok(info, run_id):
            return

        try:
            self._download_artifacts(run_id=run_id, path=info.path)
            file_path = str(Path(self.TEMP_DIR) / info.path)

            neptune_run[f"{self.BASE_NAMESPACE}/{info.path}"].upload(file_path, wait=True)

        finally:
            self._clean_up()


def get_dir_size(path: str) -> int:
    directory = Path(path)
    return sum(f.stat().st_size for f in directory.glob("**/*") if f.is_file())


class DirectoryUploadStrategy(ArtifactUploadStrategy):
    def upload_artifact(self, neptune_run: "Run", info: FileInfo, run_id: str) -> None:
        cwd = os.getcwd()

        try:
            if not info.is_dir or not self._is_size_ok(info, run_id):
                return

            os.chdir(self.TEMP_DIR)
            dir_path = str(Path(info.path) / "*")
            neptune_run[f"{self.BASE_NAMESPACE}/{info.path}"].upload_files(dir_path, wait=True)

        finally:
            os.chdir(cwd)
            self._clean_up()
