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

import click


@click.command("mlflow")
@click.option("--project", "-p", help="Neptune project name", required=False, type=str)
@click.option("--api-token", "-a", help="Your Neptune API Key", required=False, type=str)
@click.option("--mlflow-tracking-uri", "-u", help="Your MLflow tracking URI", required=False, type=str)
@click.option(
    "--exclude-artifacts",
    "-e",
    help="Specifies whether to exclude artifacts from the upload",
    required=False,
    default=False,
    type=bool,
)
@click.option(
    "--max-artifact-size",
    "-m",
    help="Maximum size uploaded to Neptune, unit is in MB",
    required=False,
    default=50,
    type=int,
)
def sync(
    *,
    project: Optional[str],
    api_token: Optional[str],
    mlflow_tracking_uri: Optional[str],
    exclude_artifacts: bool,
    max_artifact_size: int,
) -> None:
    """Exports MLflow runs to neptune.ai.

    Args:
        project: name of the Neptune project where your MLflow runs will go.
            If not provided, NEPTUNE_PROJECT env variable will be used.
        api_token: your Neptune API token.
            If not provided, NEPTUNE_API_TOKEN env variable will be used.
        mlflow_tracking_uri: your MLflow tracking URI.
            If not provided, it is left to the MLflow client to resolve it.
        exclude_artifacts: whether to skip uploading artifacts to Neptune.
        max_artifact_size: max size of the artifact to be uploaded to Neptune.
            Unit is in MB.
            For directories this will be treated as the max size of the entire directory.
    """

    # We do not want to import anything if process was executed for autocompletion purposes.
    from neptune_mlflow_exporter.impl.sync import sync as run_sync

    run_sync(
        project_name=project,
        api_token=api_token,
        mlflow_tracking_uri=mlflow_tracking_uri,
        exclude_artifacts=exclude_artifacts,
        max_artifact_size=max_artifact_size,
    )
