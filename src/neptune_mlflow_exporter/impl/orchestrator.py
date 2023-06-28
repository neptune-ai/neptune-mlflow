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

import click

try:
    from neptune import Run as NeptuneRun
except ImportError:
    from neptune.new import Run as NeptuneRun

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

    def run(self) -> None:
        fetched_data = self.fetcher.fetch_data()

        for mlflow_run in fetched_data.mlflow_runs:
            if mlflow_run.info.run_id in fetched_data.neptune_run_ids:
                click.echo(f"Ignoring mlflow_run '{mlflow_run.info.run_name}' since it already exists")
                continue

            click.echo(f"Loading mlflow_run '{mlflow_run.info.run_name}'")

            with NeptuneRun(
                project=self.config.project_name,
                api_token=self.config.api_token,
                custom_run_id=mlflow_run.info.run_id,
                capture_hardware_metrics=False,
            ) as neptune_run:
                try:
                    experiment = fetched_data.mlflow_experiments[mlflow_run.info.experiment_id]
                    self.exporter.export_experiment_metadata(neptune_run, experiment)

                    self.exporter.export_run_info(neptune_run, mlflow_run)
                    self.exporter.export_run_data(neptune_run, mlflow_run)

                    if not self.config.exclude_artifacts:
                        self.exporter.export_artifacts(
                            neptune_run, mlflow_run, self.config.max_artifact_size, self.config.mlflow_tracking_uri
                        )

                    click.echo(f"Run '{mlflow_run.info.run_name}' was saved")
                except Exception as e:
                    click.echo(f"Error exporting run '{mlflow_run.info.run_name}': {e}")
