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
from typing import Optional

import mlflow

try:
    from neptune import Project
except ImportError:
    from neptune.new.metadata_containers import Project

from neptune_mlflow_exporter.impl.components import (
    ExportConfig,
    Exporter,
    Fetcher,
)
from neptune_mlflow_exporter.impl.orchestrator import ExportOrchestrator


class NeptuneExporter:
    def __init__(
        self,
        project: Project,
        *,
        project_name: Optional[str] = None,
        api_token: Optional[str] = None,
        mlflow_tracking_uri: Optional[str] = None,
        exclude_artifacts: bool = False,
        max_artifact_size: int = 50,
    ):
        self.project = project
        self.project_name = project_name
        self.api_token = api_token
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.exclude_artifacts = exclude_artifacts
        self.max_artifact_size = int(max_artifact_size * (1024 * 1024))  # to bytes
        self.mlflow_client = mlflow.tracking.MlflowClient(tracking_uri=self.mlflow_tracking_uri)

    def run(self) -> None:
        ExportOrchestrator(
            fetcher=Fetcher(self.project, self.mlflow_client),
            exporter=Exporter(self.mlflow_client),
            config=ExportConfig(
                exclude_artifacts=self.exclude_artifacts,
                max_artifact_size=self.max_artifact_size,
                project_name=self.project_name,
                api_token=self.api_token,
                mlflow_tracking_uri=self.mlflow_tracking_uri,
            ),
        ).run()
