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
from neptune.utils import stringify_unsupported

from neptune_mlflow_exporter.impl.artifact_strategy import choose_upload_strategy

try:
    from neptune import Run as NeptuneRun
except ImportError:
    from neptune.new import Run as NeptuneRun


class Exporter:
    def __init__(self, client: mlflow.tracking.MlflowClient):
        self.mlflow_client = client

    @staticmethod
    def export_experiment_metadata(neptune_run: NeptuneRun, experiment: Experiment) -> None:
        neptune_run["experiment/experiment_id"] = experiment.experiment_id
        neptune_run["experiment/tags"] = experiment.tags
        neptune_run["experiment/name"] = experiment.name

        # https://stackoverflow.com/questions/9744775/how-to-convert-integer-timestamp-into-a-datetime
        if experiment.creation_time is not None:
            neptune_run["experiment/creation_time"] = datetime.fromtimestamp(experiment.creation_time / 1e3)

        if experiment.last_update_time is not None:
            neptune_run["experiment/last_update_time"] = datetime.fromtimestamp(experiment.last_update_time / 1e3)

    @staticmethod
    def export_run_info(neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        info = dict(mlflow_run.info)

        if mlflow_run.info.start_time is not None:
            info["start_time"] = datetime.fromtimestamp(mlflow_run.info.start_time / 1e3)

        if mlflow_run.info.end_time is not None:
            info["end_time"] = datetime.fromtimestamp(mlflow_run.info.end_time / 1e3)

        neptune_run["run_info"] = stringify_unsupported(info)
        neptune_run["sys/name"] = info["run_name"]

    def export_run_data(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        data_dict = mlflow_run.data.to_dictionary()
        if "metrics" in data_dict:
            metric_keys = data_dict["metrics"].keys()
            del data_dict["metrics"]

            for key in metric_keys:
                metrics = self.mlflow_client.get_metric_history(
                    run_id=mlflow_run.info.run_id,
                    key=key,
                )
                metric_values = list(map(lambda metric: metric.value, metrics))
                metric_timestamps = list(
                    map(lambda metric: metric.timestamp / 1e3 if metric.timestamp else None, metrics)
                )
                metric_steps = list(map(lambda metric: metric.step, metrics))

                neptune_run[f"run_data/metrics/{key}"].extend(
                    metric_values, steps=metric_steps, timestamps=metric_timestamps
                )
        neptune_run["run_data"] = data_dict

    def export_artifacts(
        self, neptune_run: NeptuneRun, mlflow_run: MlflowRun, max_artifact_size: int, tracking_uri: Optional[str]
    ) -> None:
        for artifact in self.mlflow_client.list_artifacts(run_id=mlflow_run.info.run_id):
            strategy = choose_upload_strategy(artifact, tracking_uri, max_artifact_size)

            strategy.upload_artifact(neptune_run, artifact, mlflow_run)
