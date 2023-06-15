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

__all__ = ["Exporter"]

from datetime import datetime
from typing import Optional

import mlflow
from mlflow.entities import Experiment
from mlflow.entities import Run as MlflowRun

try:
    from neptune import Run as NeptuneRun
except ImportError:
    from neptune.new.metadata_containers import Run as NeptuneRun

from neptune_mlflow_exporter.impl.artifact_strategy import (
    DirectoryUploadStrategy,
    FileUploadStrategy,
)


class Exporter:
    def __init__(self, client: mlflow.tracking.MlflowClient):
        self.mlflow_client = client

        self._cached_experiment: Optional[Experiment] = None

    def export_experiment_metadata(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        if self._cached_experiment and self._cached_experiment.experiment_id == mlflow_run.info.experiment_id:
            experiment = self._cached_experiment
        else:

            experiment = self.mlflow_client.get_experiment(experiment_id=mlflow_run.info.experiment_id)
            self._cached_experiment = experiment

        neptune_run["experiment/experiment_id"] = experiment.experiment_id
        neptune_run["experiment/tags"] = experiment.tags
        neptune_run["experiment/name"] = experiment.name

        # https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-into-a-datetime
        neptune_run["experiment/creation_time"] = datetime.fromtimestamp(experiment.creation_time / 1e3)
        neptune_run["experiment/last_update_time"] = datetime.fromtimestamp(experiment.last_update_time / 1e3)

    @staticmethod
    def export_run_info(neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        info = dict(mlflow_run.info)

        info["start_time"] = datetime.fromtimestamp(mlflow_run.info.start_time / 1e3)
        info["end_time"] = datetime.fromtimestamp(mlflow_run.info.end_time / 1e3)

        neptune_run["run_info"] = info

    def export_run_data(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        data_dict = mlflow_run.data.to_dictionary()
        metric_keys = data_dict["metrics"].keys()
        del data_dict["metrics"]

        neptune_run["run_data"] = data_dict

        for key in metric_keys:
            metric_values = [
                metric.value
                for metric in self.mlflow_client.get_metric_history(
                    run_id=mlflow_run.info.run_id,
                    key=key,
                )
            ]
            neptune_run[f"run_data/metrics/{key}"].extend(metric_values)

    def export_artifacts(
        self, neptune_run: NeptuneRun, mlflow_run: MlflowRun, max_artifact_size: int, tracking_uri: Optional[str]
    ) -> None:
        for artifact in self.mlflow_client.list_artifacts(run_id=mlflow_run.info.run_id):
            if artifact.is_dir:
                strategy = DirectoryUploadStrategy(
                    tracking_uri=tracking_uri,
                    max_file_size=max_artifact_size,
                )
            else:
                strategy = FileUploadStrategy(
                    tracking_uri=tracking_uri,
                    max_file_size=max_artifact_size,
                )

            strategy.upload_artifact(neptune_run, artifact, mlflow_run.info.run_id)
