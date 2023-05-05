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
import re
from datetime import datetime
from urllib.parse import urlparse
from urllib.request import url2pathname

import click
import mlflow
import neptune
from mlflow.entities import (
    Run,
    RunInfo,
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


def export_to_neptune(*, project: Project, mlflow_tracking_uri: str, include_artifacts: bool, max_artifact_size: int):
    mlflow_client = mlflow.tracking.MlflowClient()
    experiments = mlflow_client.search_experiments()

    experiment_ids = []
    for experiment in experiments:
        project[f"{experiment.experiment_id}/tags"] = experiment.tags
        project[f"{experiment.experiment_id}/name"] = experiment.name

        # https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-into-a-datetime
        project[f"{experiment.experiment_id}/creation_time"] = datetime.fromtimestamp(experiment.creation_time / 1e3)
        project[f"{experiment.experiment_id}/last_updated_time"] = datetime.fromtimestamp(
            experiment.last_update_time / 1e3
        )

        experiment_ids.append(experiment.experiment_id)

    mlflow_runs = mlflow_client.search_runs(experiment_ids=experiment_ids, run_view_type=ViewType.ALL)
    existing_neptune_run_ids = project.fetch_runs_table().to_pandas()["sys/custom_run_id"].to_list()

    for run in mlflow_runs:
        if run.info.run_id not in existing_neptune_run_ids:
            click.echo("Loading run {}".format(run.info.run_name))
            _export_run(run)
            click.echo("Run {} was saved".format(run.info.run_name))
        else:
            click.echo("Ignoring run {} since it already exists".format(run.info.run_name))


def _export_run(mlflow_run: Run) -> None:
    neptune_run = neptune.init_run(custom_run_id=mlflow_run.info.run_id)
    # neptune_run["run_info"] = mlflow_run.info.__dict__
    neptune_run["run_data"] = mlflow_run.data.to_dictionary()


def _get_name_for_experiment(experiment):
    return experiment.name or "experiment-{}".format(experiment.experiment_id)


def _get_run_qualified_name(experiment, mlflow_run_info: RunInfo):
    exp_name = _get_name_for_experiment(experiment)
    return "{}/{}".format(exp_name, mlflow_run_info.run_id)


def _to_proper_tag(tag: str):
    return re.sub("[^a-zA-Z0-9\\-_]", "_", tag).lower()


def _get_metric_file(experiment, run_info: RunInfo, metric_key: str):
    return "mlruns/{}/{}/metrics/{}".format(experiment.experiment_id, run_info.run_uuid, metric_key)


def _get_mlflow_run_name(mlflow_run: Run):
    return mlflow_run.data.tags.get("mlflow.runName", None)


def _create_metric(neptune_exp, experiment, mlflow_run: Run, metric_key: str):
    with open(_get_metric_file(experiment, mlflow_run.info, metric_key)) as f:
        for idx, line in enumerate(f, start=1):
            value = float(line.split()[1])
            neptune_exp.send_metric(metric_key, idx, value)


def _get_params(mlflow_run: Run):
    params = {}
    for key, value in mlflow_run.data.params.items():
        params[key] = value
    return params


def _create_neptune_experiment(project: Project, experiment, mlflow_run: Run):
    with project.create_experiment(
        name=_get_name_for_experiment(experiment),
        params=_get_params(mlflow_run),
        properties=_get_properties(experiment, mlflow_run),
        tags=_get_tags(experiment, mlflow_run),
        upload_source_files=[],
        abort_callback=lambda *args: None,
        upload_stdout=False,
        upload_stderr=False,
        send_hardware_metrics=False,
        run_monitoring_thread=False,
        handle_uncaught_exceptions=True,
    ) as neptune_exp:
        if mlflow_run.info.artifact_uri.startswith("file:/"):
            artifacts_path = url2pathname(urlparse(mlflow_run.info.artifact_uri).path)
            for artifact in os.listdir(artifacts_path):
                neptune_exp.send_artifact(artifact)
        else:
            click.echo(
                "WARNING: Remote artifacts are not supported and won't be uploaded (artifact_uri: {}).".format(
                    mlflow_run.info.artifact_uri
                )
            )

        for metric_key in mlflow_run.data.metrics.keys():
            _create_metric(neptune_exp, experiment, mlflow_run, metric_key)

        return neptune_exp.id


def _get_properties(experiment, mlflow_run: Run):
    properties = {
        MLFLOW_EXPERIMENT_ID_PROPERTY: str(experiment.experiment_id),
        MLFLOW_EXPERIMENT_NAME_PROPERTY: experiment.name,
        MLFLOW_RUN_ID_PROPERTY: mlflow_run.info.run_uuid,
        MLFLOW_RUN_NAME_PROPERTY: _get_mlflow_run_name(mlflow_run) or "",
    }
    for key, value in mlflow_run.data.tags.items():
        properties[key] = value
    return properties


def _get_tags(experiment, mlflow_run: Run):
    tags = [_to_proper_tag(experiment.name), "mlflow"]
    if _get_mlflow_run_name(mlflow_run):
        tags.append(_to_proper_tag(_get_mlflow_run_name(mlflow_run)))
    return tags
