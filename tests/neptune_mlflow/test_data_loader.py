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
import uuid

from mock import MagicMock

from neptune_mlflow.data_loader import DataLoader


class TestDataLodaer(unittest.TestCase):

    def test_get_run_qualified_name(self):
        # given
        exp = MagicMock()
        exp.name = 'exp_name'

        # and
        run_info = MagicMock()
        run_info.name = None
        run_info.run_id = 'run_uuid'

        # expect
        # pylint: disable=protected-access
        self.assertEqual(DataLoader._get_run_qualified_name(exp, run_info), "exp_name/run_uuid")

    def test_get_metric_file(self):
        # given
        exp = MagicMock()
        exp.experiment_id = 'exp_id'

        # and
        run_info = MagicMock()
        run_info.run_uuid = 'run_uuid'

        # and
        metric_key = 'metric_key'

        # expect
        # pylint: disable=protected-access
        self.assertEqual(
            DataLoader._get_metric_file(exp, run_info, metric_key),
            "mlruns/exp_id/run_uuid/metrics/metric_key")

    def test_get_tags(self):
        # given
        exp = MagicMock()
        exp.name = 'EXPeriMENT-NaMe'

        # and
        run = MagicMock()
        run.info = MagicMock()
        run.data.tags = {}

        # expect
        # pylint: disable=protected-access
        self.assertEqual(
            set(DataLoader._get_tags(exp, run)),
            {'mlflow', 'experiment-name'})

    def test_get_properties(self):
        # given
        exp = MagicMock()
        exp.experiment_id = 123
        exp.name = 'EXPeriMENT-NaMe'

        # and
        run = MagicMock()

        # and
        run.info = MagicMock()
        run.info.run_uuid = str(uuid.uuid4())

        # and
        run.data = MagicMock()
        run.data.tags = {
            'key1': 'value1',
            'key2': 'value2'
        }

        # expect
        # pylint: disable=protected-access
        self.assertEqual(
            DataLoader._get_properties(exp, run),
            {
                'mlflow/experiment/id': str(exp.experiment_id),
                'mlflow/experiment/name': exp.name,
                'mlflow/run/uuid': run.info.run_uuid,
                'mlflow/run/name': '',
                'key1': 'value1',
                'key2': 'value2'
            }
        )

    def test_get_params(self):
        # given
        run = MagicMock()
        run.data = MagicMock()
        run.data.params = {
            'key1': 'value1',
            'key2': 'value2'
        }

        # expect
        # pylint: disable=protected-access
        self.assertEqual(
            DataLoader._get_params(run),
            {
                'key1': 'value1',
                'key2': 'value2'
            }
        )
