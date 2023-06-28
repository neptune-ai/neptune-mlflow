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

__all__ = ["Fetcher"]

from dataclasses import dataclass
from typing import (
    List,
    MutableMapping,
    Set,
)

import mlflow
from mlflow.entities import Experiment
from mlflow.entities import Run as MlflowRun
from mlflow.entities import ViewType
from neptune import Project


@dataclass
class FetchedData:
    mlflow_experiments: MutableMapping[str, Experiment]
    mlflow_runs: List[MlflowRun]
    neptune_run_ids: Set[str]


class Fetcher:
    def __init__(self, project: Project, client: mlflow.tracking.MlflowClient):
        self.project = project
        self.mlflow_client = client

    def get_all_mlflow_experiments(self) -> MutableMapping[str, Experiment]:
        page_limit = 100
        all_experiments = []
        page_token = None

        experiment_mapping = {}

        while not all_experiments or page_token:
            experiments = self.mlflow_client.search_experiments(
                max_results=page_limit, page_token=page_token, view_type=ViewType.ACTIVE_ONLY
            )

            all_experiments.extend(experiments)
            page_token = experiments.token

        for exp in all_experiments:
            experiment_mapping[exp.experiment_id] = exp

        return experiment_mapping

    def get_all_mlflow_runs(self, experiment_ids: List[str]) -> List[MlflowRun]:
        page_limit = 100
        all_runs = []
        page_token = None

        while not all_runs or page_token:
            runs = self.mlflow_client.search_runs(
                experiment_ids=experiment_ids, run_view_type=ViewType.ALL, max_results=page_limit, page_token=page_token
            )

            all_runs.extend(runs)

            page_token = runs.token

        return all_runs

    def get_existing_neptune_run_ids(self) -> Set[str]:
        try:
            existing_neptune_run_ids = {
                run_id for run_id in self.project.fetch_runs_table().to_pandas()["sys/custom_run_id"].to_list()
            }
        except KeyError:
            # empty project
            existing_neptune_run_ids = set()

        return existing_neptune_run_ids

    def fetch_data(self) -> FetchedData:
        experiments = self.get_all_mlflow_experiments()

        experiment_ids = list(experiments.keys())

        mlflow_runs = self.get_all_mlflow_runs(experiment_ids)

        neptune_run_ids = self.get_existing_neptune_run_ids()

        return FetchedData(
            mlflow_experiments=experiments,
            mlflow_runs=mlflow_runs,
            neptune_run_ids=neptune_run_ids,
        )
