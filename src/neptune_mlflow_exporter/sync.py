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
import os
from typing import Optional

import neptune

from neptune_mlflow_exporter import NeptuneExporter


def sync(
    project_name: Optional[str] = None,
    api_token: Optional[str] = None,
    mlflow_tracking_uri: Optional[str] = None,
    exclude_artifacts: bool = True,
    max_artifact_size: int = 50,
) -> None:

    if not isinstance(max_artifact_size, int):
        raise TypeError(f"Invalid type for `max_artifact_size`. Expected int, got {type(max_artifact_size)} instead.")

    if max_artifact_size <= 0:
        raise ValueError("Max artifact size must be a positive integer")

    if project_name:
        os.environ["NEPTUNE_PROJECT"] = project_name
    if api_token:
        os.environ["NEPTUNE_API_KEY"] = api_token

    project = neptune.init_project()

    NeptuneExporter(
        project=project,
        mlflow_tracking_uri=mlflow_tracking_uri,
        exclude_artifacts=exclude_artifacts,
        max_artifact_size=max_artifact_size,
    ).run()
