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

__all__ = ["ExportOrchestrator"]

from typing import List

import click

try:
    from neptune import Run as NeptuneRun
except ImportError:
    from neptune.new import Run as NeptuneRun

from mlflow.entities import Run as MlflowRun

from neptune_mlflow_exporter.impl.components import (
    ExportConfig,
    Exporter,
    Fetcher,
)


class ExportOrchestrator:
    def __init__(self, fetcher: Fetcher, exporter: Exporter, config: ExportConfig):

        self.fetcher = fetcher
        self.exporter = exporter
        self.config = config

    def _fetch_runs(self) -> List[MlflowRun]:
        try:
            experiments = self.fetcher.get_all_mlflow_experiments()

            experiment_ids = [experiment.experiment_id for experiment in experiments]

            mlflow_runs = self.fetcher.get_all_mlflow_runs(experiment_ids)

            return mlflow_runs
        except Exception as e:
            click.echo(f"Error during mlflow data fetching: {e}")
            return []

    def _export_data(self, neptune_run: NeptuneRun, mlflow_run: MlflowRun) -> None:
        self.exporter.export_experiment_metadata(neptune_run, mlflow_run)
        self.exporter.export_run_info(neptune_run, mlflow_run)
        self.exporter.export_run_data(neptune_run, mlflow_run)

        if not self.config.exclude_artifacts:
            self.exporter.export_artifacts(
                neptune_run, mlflow_run, self.config.max_artifact_size, self.config.mlflow_tracking_uri
            )

    def run(self) -> None:
        mlflow_runs = self._fetch_runs()
        existing_neptune_run_ids = self.fetcher.get_existing_neptune_run_ids()

        for mlflow_run in mlflow_runs:
            if mlflow_run.info.run_id in existing_neptune_run_ids:
                click.echo(f"Ignoring mlflow_run '{mlflow_run.info.run_name}' since it already exists")
                continue

            click.echo(f"Loading mlflow_run '{mlflow_run.info.run_name}'")

            with NeptuneRun(
                project=self.config.project_name, api_token=self.config.api_token, custom_run_id=mlflow_run.info.run_id
            ) as neptune_run:
                try:
                    self._export_data(neptune_run, mlflow_run)

                    click.echo(f"Run '{mlflow_run.info.run_name}' was saved")
                except Exception as e:
                    click.echo(f"Error exporting run '{mlflow_run.info.run_name}': {e}")
