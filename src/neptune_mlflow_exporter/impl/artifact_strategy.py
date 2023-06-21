#
# Copyright (c) 2023, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

__all__ = [
    "FileUploadStrategy",
    "DirectoryUploadStrategy",
    "choose_upload_strategy",
]

import contextlib
import os
import tempfile
from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path
from typing import TYPE_CHECKING

from mlflow.artifacts import download_artifacts
from mlflow.entities import FileInfo
from mlflow.entities import Run as MlflowRun

if TYPE_CHECKING:
    try:
        from neptune import Run
    except ImportError:
        from neptune.new import Run


def get_dir_size(path: str) -> int:
    directory = Path(path)
    return sum(f.stat().st_size for f in directory.glob("**/*") if f.is_file())


@contextlib.contextmanager
def preserve_cwd(path):
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


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
    def upload_to_neptune(self, neptune_run: "Run", info: FileInfo) -> None:
        ...

    def upload_artifact(self, neptune_run: "Run", info: FileInfo, mlflow_run: MlflowRun) -> None:
        with tempfile.TemporaryDirectory() as tmpdirname:
            with preserve_cwd(tmpdirname):
                if not info.is_dir and info.file_size > self._max_size:
                    return

                artifact_uri = mlflow_run.info.artifact_uri
                download_artifacts(artifact_uri=artifact_uri + "/" + info.path, dst_path=tmpdirname)

                if info.is_dir and get_dir_size(tmpdirname) > self._max_size:
                    return

                self.upload_to_neptune(neptune_run, info)


class FileUploadStrategy(ArtifactUploadStrategy):
    def upload_to_neptune(self, neptune_run: "Run", info: FileInfo) -> None:
        neptune_run[f"{self.BASE_NAMESPACE}/{info.path}"].upload(info.path, wait=True)


class DirectoryUploadStrategy(ArtifactUploadStrategy):
    def upload_to_neptune(self, neptune_run: "Run", info: FileInfo) -> None:
        dir_path = str(Path(info.path) / "*")
        neptune_run[f"{self.BASE_NAMESPACE}/{info.path}"].upload_files(dir_path, wait=True)


def choose_upload_strategy(artifact: FileInfo, tracking_uri: str, max_artifact_size: int) -> ArtifactUploadStrategy:
    if artifact.is_dir:
        return DirectoryUploadStrategy(
            tracking_uri=tracking_uri,
            max_file_size=max_artifact_size,
        )
    else:
        return FileUploadStrategy(
            tracking_uri=tracking_uri,
            max_file_size=max_artifact_size,
        )
