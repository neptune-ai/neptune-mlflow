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
import unittest
from unittest.mock import patch

from click.testing import CliRunner

from neptune_mlflow_plugin import sync


class TestPlugin(unittest.TestCase):
    runner = CliRunner()

    @patch("neptune_mlflow.sync.sync")
    def test_sync_called_once(self, mock_sync):
        result = self.runner.invoke(sync)

        self.assertEqual(result.exit_code, 0)

        mock_sync.assert_called_once_with(
            project_name=None, api_token=None, mlflow_tracking_uri=None, include_artifacts=False, max_artifact_size=50
        )

    def test_invalid_max_artifact_size(self):
        result = self.runner.invoke(sync, ["-m", -100])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, ValueError)

        result = self.runner.invoke(sync, ["-m", 0])
        self.assertEqual(result.exit_code, 1)
        self.assertIsInstance(result.exception, ValueError)
