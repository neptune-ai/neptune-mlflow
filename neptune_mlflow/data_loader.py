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
from __future__ import print_function

import os
import click
import mlflow
import path as path_utils

class DataLoader(object):

    MLFLOW_EXPERIMENT_ID_PROPERTY = "mlflow/experiment/id"
    MLFLOW_EXPERIMENT_NAME_PROPERTY = "mlflow/experiment/name"
    MLFLOW_RUN_ID_PROPERTY = "mlflow/run/uuid"
    MLFLOW_RUN_NAME_PROPERTY = "mlflow/run/name"

    def __init__(self, project, path):
        self._project = project
        self._path = path

    def run(self):
        with path_utils.Path(self._path):
            mlflow_client = mlflow.tracking.MlflowClient()
            experiments = mlflow_client.list_experiments()

            for experiment in experiments:
                run_infos = mlflow_client.list_run_infos(experiment_id=experiment.experiment_id)
                existing_experiments = self._project.get_experiments(tag=experiment.name.lower())
                existing_run_uuids = set([
                    str(e.get_properties().get(DataLoader.MLFLOW_RUN_ID_PROPERTY)) for e in existing_experiments
                ])

                for run_info in run_infos:
                    run_qualified_name = self._get_run_qualified_name(experiment, run_info)
                    if run_info.run_uuid not in existing_run_uuids:
                        click.echo("Loading run {}".format(run_qualified_name))
                        run = mlflow_client.get_run(run_info.run_uuid)
                        exp_uuid = self._create_neptune_experiment(experiment, run)
                        click.echo("Run {} was saved as {}".format(run_qualified_name, exp_uuid))
                    else:
                        click.echo("Ignoring run {} since it already exists".format(run_qualified_name))

    def _create_neptune_experiment(self, experiment, run):
        with self._project.create_experiment(
            name=self._get_name_for_experiment(experiment),
            params=self._get_params(run),
            properties=self._get_properties(experiment, run),
            tags=self._get_tags(experiment, run),
            upload_source_files=[],
            abort_callback=lambda *args: None,
            upload_stdout=False,
            upload_stderr=False,
            send_hardware_metrics=False,
            run_monitoring_thread=False,
            handle_uncaught_exceptions=True
        ) as neptune_exp:
            if run.info.artifact_uri.startswith('file:/'):
                artifacts_path = run.info.artifact_uri[6:]
                with path_utils.Path(artifacts_path):
                    for artifact in os.listdir(artifacts_path):
                        neptune_exp.send_artifact(artifact)
            else:
                click.echo('WARNING: Remote artifacts are not supported and won\'t be uploaded (artifact_uri: {}).'
                           .format(run.info.artifact_uri))

            for metric_key in run.data.metrics.keys():
                self._create_metric(neptune_exp, experiment, run, metric_key)

            return neptune_exp.id

    @staticmethod
    def _create_metric(neptune_exp, experiment, run, metric_key):
        with open(DataLoader._get_metric_file(experiment, run.info, metric_key)) as f:
            for idx, line in enumerate(f, start=1):
                value = float(line.split()[1])
                neptune_exp.send_metric(metric_key, idx, value)

    @staticmethod
    def _get_params(run):
        params = {}
        for key, value in run.data.params.items():
            params[key] = value
        return params

    @staticmethod
    def _get_properties(experiment, run):
        properties = {
            DataLoader.MLFLOW_EXPERIMENT_ID_PROPERTY: str(experiment.experiment_id),
            DataLoader.MLFLOW_EXPERIMENT_NAME_PROPERTY: experiment.name,
            DataLoader.MLFLOW_RUN_ID_PROPERTY: run.info.run_uuid,
            DataLoader.MLFLOW_RUN_NAME_PROPERTY: DataLoader._get_mlflow_run_name(run) or ''
        }
        for key, value in run.data.tags.items():
            properties[key] = value
        return properties

    @staticmethod
    def _get_tags(experiment, run):
        tags = [experiment.name.lower(), 'mlflow']
        if DataLoader._get_mlflow_run_name(run):
            tags.append(DataLoader._get_mlflow_run_name(run).lower())
        return tags

    @staticmethod
    def _get_metric_file(experiment, run_info, metric_key):
        return "mlruns/{}/{}/metrics/{}".format(experiment.experiment_id, run_info.run_uuid, metric_key)

    @staticmethod
    def _get_name_for_experiment(experiment):
        return experiment.name or "experiment-{}".format(experiment.experiment_id)

    @staticmethod
    def _get_run_qualified_name(experiment, run_info):
        exp_name = DataLoader._get_name_for_experiment(experiment)
        return "{}/{}".format(exp_name, run_info.run_id)

    @staticmethod
    def _get_mlflow_run_name(run):
        return run.data.tags.get('mlflow.runName', None)
