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
from typing import Set

import click
import mlflow
import neptune
from mlflow.entities import Experiment
from mlflow.entities import Run as MlflowRun
from mlflow.entities import ViewType
from mlflow.tracking.artifact_utils import get_artifact_uri

try:
    from neptune import Project
    from neptune import Run as NeptuneRun
except ImportError:
    from neptune.new.metadata_containers import Project
    from neptune.new.metadata_containers import Run as NeptuneRun


class NeptuneExporter:
    def __init__(
        self, *, project: Project, mlflow_tracking_uri: str, include_artifacts: bool, max_artifact_size: int = 50
    ):
        self.project = project
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.include_artifacts = include_artifacts
        self.max_artifact_size = max_artifact_size * 2e20  # to bytes

        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        self.mlflow_client = mlflow.tracking.MlflowClient()

    def run(self) -> None:

        experiments = self.mlflow_client.search_experiments()

        experiment_ids = []
        for experiment in experiments:
            self._export_project_metadata(experiment)

            experiment_ids.append(experiment.experiment_id)

        mlflow_runs = self.mlflow_client.search_runs(experiment_ids=experiment_ids, run_view_type=ViewType.ALL)

        existing_neptune_run_ids = self._get_existing_neptune_run_ids()

        for mlflow_run in mlflow_runs:
            if mlflow_run.info.run_id not in existing_neptune_run_ids:
                click.echo("Loading mlflow_run {}".format(mlflow_run.info.run_name))
                with neptune.init_run(custom_run_id=mlflow_run.info.run_id) as neptune_run:
                    self._export_run(neptune_run, mlflow_run)

                    if self.include_artifacts:
                        self._export_artifacts(neptune_run, mlflow_run)

                        click.echo("Run {} was saved".format(mlflow_run.info.run_name))
                    else:
                        click.echo("Ignoring mlflow_run {} since it already exists".format(mlflow_run.info.run_name))

    def _get_existing_neptune_run_ids(self) -> Set[str]:
        try:
            existing_neptune_run_ids = {
                run_id for run_id in self.project.fetch_runs_table().to_pandas()["sys/custom_run_id"].to_list()
            }
        except KeyError:
            # empty project
            existing_neptune_run_ids = set()

        return existing_neptune_run_ids

    def _export_project_metadata(self, experiment: Experiment) -> None:
        self.project[f"{experiment.experiment_id}/experiment_id"] = experiment.experiment_id
        self.project[f"{experiment.experiment_id}/tags"] = experiment.tags
        self.project[f"{experiment.experiment_id}/name"] = experiment.name

        # https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-into-a-datetime
        self.project[f"{experiment.experiment_id}/creation_time"] = datetime.fromtimestamp(
            experiment.creation_time / 1e3
        )
        self.project[f"{experiment.experiment_id}/last_updated_time"] = datetime.fromtimestamp(
            experiment.last_update_time / 1e3
        )

    def _export_run(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        info = dict(mlflow_run.info)

        if "start_time" in info:
            neptune_run["run_info/start_time"] = datetime.fromtimestamp(mlflow_run.info.start_time / 1e3)
            del info["start_time"]
        if "end_time" in info:
            neptune_run["run_info/end_time"] = datetime.fromtimestamp(mlflow_run.info.end_time / 1e3)
            del info["end_time"]

        neptune_run["run_info"] = info

        self._export_metrics(neptune_run, mlflow_run)

        data_dict = mlflow_run.data.to_dictionary()
        del data_dict["metrics"]
        neptune_run["run_data"] = data_dict

    def _export_metrics(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        metric_keys = mlflow_run.data.to_dictionary()["metrics"].keys()

        for key in metric_keys:
            metric_values = [
                metric.value
                for metric in self.mlflow_client.get_metric_history(
                    run_id=mlflow_run.info.run_id,
                    key=key,
                )
            ]
            for val in metric_values:
                neptune_run[f"run_data/metrics/{key}"].append(val)

    def _export_artifacts(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        for artifact in self.mlflow_client.list_artifacts(run_id=mlflow_run.info.run_id):
            if artifact.is_dir or artifact.file_size > self.max_artifact_size:
                continue
            path = artifact.path
            uri = get_artifact_uri(run_id=mlflow_run.info.run_id, artifact_path=path)
            neptune_run[path].track_files(uri)
