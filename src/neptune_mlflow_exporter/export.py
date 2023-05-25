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
from typing import (
    Optional,
    Set,
)

import click
import mlflow
import neptune
from mlflow.entities import Run as MlflowRun
from mlflow.entities import ViewType

try:
    from neptune import Project
    from neptune import Run as NeptuneRun
except ImportError:
    from neptune.new.metadata_containers import Project
    from neptune.new.metadata_containers import Run as NeptuneRun

from neptune_mlflow_exporter.utils import (
    DirectoryUploadStrategy,
    FileUploadStrategy,
)


class NeptuneExporter:
    def __init__(
        self,
        project: Project,
        *,
        mlflow_tracking_uri: Optional[str] = None,
        exclude_artifacts: bool = False,
        max_artifact_size: int = 50,
    ):
        self.project = project
        self.mlflow_tracking_uri = mlflow_tracking_uri
        self.exclude_artifacts = exclude_artifacts
        self.max_artifact_size = int(max_artifact_size * 2e20)  # to bytes

        mlflow.set_tracking_uri(self.mlflow_tracking_uri)
        self.mlflow_client = mlflow.tracking.MlflowClient()

    def run(self) -> None:

        experiments = self.mlflow_client.search_experiments()

        experiment_ids = [experiment.experiment_id for experiment in experiments]

        mlflow_runs = self.mlflow_client.search_runs(experiment_ids=experiment_ids, run_view_type=ViewType.ALL)

        existing_neptune_run_ids = self._get_existing_neptune_run_ids()

        for mlflow_run in mlflow_runs:
            if mlflow_run.info.run_id not in existing_neptune_run_ids:
                click.echo("Loading mlflow_run {}".format(mlflow_run.info.run_name))
                with neptune.init_run(custom_run_id=mlflow_run.info.run_id) as neptune_run:

                    self._export_experiment_metadata(neptune_run, mlflow_run)
                    self._export_run_info(neptune_run, mlflow_run)
                    self._export_run_data(neptune_run, mlflow_run)

                    if not self.exclude_artifacts:
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

    def _export_experiment_metadata(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        experiment = self.mlflow_client.get_experiment(experiment_id=mlflow_run.info.experiment_id)
        neptune_run["experiment/experiment_id"] = experiment.experiment_id
        neptune_run["experiment/tags"] = experiment.tags
        neptune_run["experiment/name"] = experiment.name

        # https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-into-a-datetime
        neptune_run["experiment/creation_time"] = datetime.fromtimestamp(experiment.creation_time / 1e3)
        neptune_run["experiment/last_update_time"] = datetime.fromtimestamp(experiment.last_update_time / 1e3)

    @staticmethod
    def _export_run_info(neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        info = dict(mlflow_run.info)

        if "start_time" in info:
            neptune_run["run_info/start_time"] = datetime.fromtimestamp(mlflow_run.info.start_time / 1e3)
            del info["start_time"]
        if "end_time" in info:
            neptune_run["run_info/end_time"] = datetime.fromtimestamp(mlflow_run.info.end_time / 1e3)
            del info["end_time"]

        neptune_run["run_info"] = info

    def _export_run_data(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        data_dict = mlflow_run.data.to_dictionary()
        metric_keys = data_dict["metrics"].keys()

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

        del data_dict["metrics"]
        neptune_run["run_data"] = data_dict

    def _export_artifacts(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        for artifact in self.mlflow_client.list_artifacts(run_id=mlflow_run.info.run_id):
            if artifact.is_dir:
                strategy = DirectoryUploadStrategy(
                    tracking_uri=self.mlflow_tracking_uri,
                    max_file_size=self.max_artifact_size,
                )
            else:
                strategy = FileUploadStrategy(
                    tracking_uri=self.mlflow_tracking_uri,
                    max_file_size=self.max_artifact_size,
                )

            strategy.upload_artifact(neptune_run, artifact, mlflow_run.info.run_id)
