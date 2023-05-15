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
import datetime
import os
import unittest
from unittest.mock import (
    MagicMock,
    Mock,
    patch,
)

import mlflow.tracking

from neptune_mlflow.export import (
    export_project_metadata,
    export_run,
)


class MockClient(MagicMock):
    def search_experiments(self, experiment_ids):
        return [MagicMock() for _ in range(len(experiment_ids))]

    def search_runs(self, experiment_ids, **kwargs):
        return [MagicMock() for _ in range(len(experiment_ids))]

    def list_artifacts(self, run_id):
        return [MagicMock(), MagicMock()]


class MockExperiment(MagicMock):
    @property
    def experiment_id(self):
        return "ex1"

    @property
    def tags(self) -> dict:
        return {
            "tag1": "val1",
            "tag2": "val2",
        }

    @property
    def name(self) -> str:
        return "Test Experiment"

    @property
    def creation_time(self) -> int:
        return 1683197418954

    @property
    def last_update_time(self) -> int:
        return 1683197418954


class MockRun(MagicMock):
    class Info(MagicMock):
        @property
        def run_id(self) -> str:
            return "testRun1"

        @property
        def start_time(self) -> int:
            return 1683197418954

        @property
        def end_time(self) -> int:
            return 1683197438954

    class Data(MagicMock):
        def to_dictionary(self) -> dict:
            return {
                "metrics": {
                    "metric1": "value1",
                    "metric2": "value2",
                },
            }

    @property
    def info(self):
        return self.Info()

    @property
    def data(self):
        return self.Data()


class MockNeptuneRun(Mock):
    storage = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __getitem__(self, item):
        return self.storage[item]

    def __setitem__(self, key, value):
        self.storage[key] = value


class TestNeptuneExport(unittest.TestCase):
    def setUp(self) -> None:
        self.current_neptune_mode = os.getenv("NEPTUNE_MODE", None)
        os.environ["NEPTUNE_MODE"] = "debug"

    def test_export_project_metadata(self) -> None:
        with patch("neptune.Project", {}) as mock_project, patch(
            "mlflow.entities.Experiment", MockExperiment()
        ) as mock_experiment:
            export_project_metadata(mock_project, mock_experiment)
            assert mock_project["ex1/tags"] == mock_experiment.tags

            assert mock_project["ex1/name"] == mock_experiment.name

            assert mock_project["ex1/creation_time"] == datetime.datetime(2023, 5, 4, 12, 50, 18, 954000)

            assert mock_project["ex1/last_updated_time"] == datetime.datetime(2023, 5, 4, 12, 50, 18, 954000)

    def test_export_run(self) -> None:
        with patch("mlflow.tracking.MlflowClient.get_metric_history") as mock_get_history, patch(
            "mlflow.entities.Run", MockRun()
        ) as mock_mlflow_run, patch(
            "neptune.Run",
            MockNeptuneRun(),
        ) as mock_neptune_run:
            mock_get_history.return_value = mock_mlflow_run.data.to_dictionary()
            export_run(mock_mlflow_run, mlflow.tracking.MlflowClient())

            assert mock_neptune_run.storage["run_info/run_id"] == mock_mlflow_run.info.run_id

            assert mock_neptune_run["run_info/start_time"] == datetime.datetime.fromtimestamp(
                mock_mlflow_run.info.start_time / 1e3
            )

            assert mock_neptune_run["run_data"] == mock_mlflow_run.data.to_dictionary()

    def tearDown(self) -> None:
        if self.current_neptune_mode:
            os.environ["NEPTUNE_MODE"] = self.current_neptune_mode
        else:
            del os.environ["NEPTUNE_MODE"]
