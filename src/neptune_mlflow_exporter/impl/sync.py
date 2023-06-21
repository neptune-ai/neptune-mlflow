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

try:
    from neptune import init_project
    from neptune.integrations.utils import verify_type
except ImportError:
    from neptune.new import init_project
    from neptune.new.integrations.utils import verify_type

from neptune_mlflow_exporter.impl import NeptuneExporter


def sync(
    project_name: Optional[str] = None,
    api_token: Optional[str] = None,
    mlflow_tracking_uri: Optional[str] = None,
    exclude_artifacts: bool = False,
    max_artifact_size: int = 50,
) -> None:

    verify_type("max_artifact_size", max_artifact_size, int)

    if max_artifact_size <= 0:
        raise ValueError("Max artifact size must be a positive integer")

    with init_project(project=project_name, api_token=api_token) as project:
        NeptuneExporter(
            project=project,
            project_name=project_name,
            api_token=api_token,
            mlflow_tracking_uri=mlflow_tracking_uri,
            exclude_artifacts=exclude_artifacts,
            max_artifact_size=max_artifact_size,
        ).run()
