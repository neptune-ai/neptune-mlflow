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

import click


@click.command("mlflow")
@click.option("--project", "-p", help="Neptune project name", required=False, type=str)
@click.option("--api-token", "-a", help="Your Neptune API Key", required=False, type=str)
@click.option("--mlflow-tracking-uri", "-u", help="Your MLflow tracking URI", required=False, type=str)
@click.option(
    "--include-artifacts",
    "-i",
    help="Specifies whether to also include artifacts in the upload",
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
def sync(project: str, api_token: str, mlflow_tracking_uri: str, include_artifacts: bool, max_artifact_size: int):
    """Upload mlflow runs data to Neptune.
    PATH is a directory where Neptune will look for `mlruns` directory with mlflow data.

    Examples:

        neptune mlflow .

        neptune mlflow /path

        neptune mlflow /path --project username/sandbox

    """

    # We do not want to import anything if process was executed for autocompletion purposes.
    from neptune_mlflow.sync import sync as run_sync

    return run_sync(
        project_name=project,
        api_token=api_token,
        mlflow_tracking_uri=mlflow_tracking_uri,
        include_artifacts=include_artifacts,
        max_artifact_size=max_artifact_size,
    )
