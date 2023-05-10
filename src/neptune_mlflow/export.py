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
from datetime import datetime

import click
import mlflow
import neptune
from mlflow.entities import (
    Experiment,
    Run,
    ViewType,
)

try:
    from neptune import Project
except ImportError:
    from neptune.new.metadata_containers import Project

MLFLOW_EXPERIMENT_ID_PROPERTY = "mlflow/experiment/id"
MLFLOW_EXPERIMENT_NAME_PROPERTY = "mlflow/experiment/name"
MLFLOW_RUN_ID_PROPERTY = "mlflow/run/uuid"
MLFLOW_RUN_NAME_PROPERTY = "mlflow/run/name"


def export_to_neptune(
    *, project: Project, mlflow_tracking_uri: str, include_artifacts: bool, max_artifact_size: int = 50
):

    max_artifact_size *= 2e20  # to bytes

    mlflow_client = mlflow.tracking.MlflowClient(tracking_uri=mlflow_tracking_uri)
    experiments = mlflow_client.search_experiments()

    experiment_ids = []
    for experiment in experiments:
        export_project_metadata(project, experiment)

        experiment_ids.append(experiment.experiment_id)

    mlflow_runs = mlflow_client.search_runs(experiment_ids=experiment_ids, run_view_type=ViewType.ALL)
    existing_neptune_run_ids = {
        run_id for run_id in project.fetch_runs_table().to_pandas()["sys/custom_run_id"].to_list()
    }

    for run in mlflow_runs:
        if run.info.run_id not in existing_neptune_run_ids:
            click.echo("Loading run {}".format(run.info.run_name))
            export_run(run)

            if include_artifacts:
                artifacts = mlflow_client.list_artifacts(run_id=run.info.run_id)
                for artifact in artifacts:
                    if not artifact.is_dir and artifact.file_size <= max_artifact_size:
                        mlflow_client.download_artifacts(run_id=run.info.run_id, path=artifact.path)
                        # logic to upload file to Neptune
            click.echo("Run {} was saved".format(run.info.run_name))
        else:
            click.echo("Ignoring run {} since it already exists".format(run.info.run_name))


def export_project_metadata(project: Project, experiment: Experiment) -> None:
    project[f"{experiment.experiment_id}/tags"] = experiment.tags
    project[f"{experiment.experiment_id}/name"] = experiment.name

    # https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-into-a-datetime
    project[f"{experiment.experiment_id}/creation_time"] = datetime.fromtimestamp(experiment.creation_time / 1e3)
    project[f"{experiment.experiment_id}/last_updated_time"] = datetime.fromtimestamp(experiment.last_update_time / 1e3)


def export_run(mlflow_run: Run) -> None:
    with neptune.Run(custom_run_id=mlflow_run.info.run_id) as neptune_run:
        neptune_run["run_info/run_id"] = mlflow_run.info.run_id
        neptune_run["run_info/experiment_id"] = mlflow_run.info.experiment_id
        neptune_run["run_info/run_uuid"] = mlflow_run.info.run_uuid
        neptune_run["run_info/run_name"] = mlflow_run.info.run_name
        neptune_run["run_info/user_id"] = mlflow_run.info.user_id
        neptune_run["run_info/status"] = mlflow_run.info.status
        neptune_run["run_info/start_time"] = datetime.fromtimestamp(mlflow_run.info.start_time / 1e3)
        neptune_run["run_info/end_time"] = datetime.fromtimestamp(mlflow_run.info.end_time / 1e3)
        neptune_run["run_info/lifecycle_stage"] = mlflow_run.info.lifecycle_stage

        neptune_run["run_data"] = mlflow_run.data.to_dictionary()
