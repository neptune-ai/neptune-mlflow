#
# Copyright (c) 2019, Neptune Labs Sp. z o.o.
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
import neptune

from neptune_mlflow import export_to_neptune


def sync(
    project_name: str, api_token: str, mlflow_tracking_uri: str, include_artifacts: bool, max_artifact_size: int
) -> None:

    project = neptune.init_project(project=project_name, api_token=api_token)

    export_to_neptune(
        project=project,
        mlflow_tracking_uri=mlflow_tracking_uri,
        include_artifacts=include_artifacts,
        max_artifact_size=max_artifact_size,
    )
