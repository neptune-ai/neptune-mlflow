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

from collections import namedtuple
from mock import MagicMock

from cli.data_loader import DataLoader


class TestDataLodaer(unittest.TestCase):

    def test_get_run_qualified_name(self):
        # given
        exp = MagicMock()
        exp.name = 'exp_name'
        run_info = MagicMock()
        run_info.name = None
        run_info.run_uuid = 'run_uuid'

        # then
        # pylint: disable=protected-access
        self.assertEqual(DataLoader._get_run_qualified_name(exp, run_info), "exp_name/run_uuid")

    def test_get_metric_file(self):
        # given
        exp = MagicMock()
        exp.experiment_id = 'exp_id'
        run_info = MagicMock()
        run_info.run_uuid = 'run_uuid'
        metric_key = 'metric_key'

        # then
        # pylint: disable=protected-access
        self.assertEqual(
            DataLoader._get_metric_file(exp, run_info, metric_key),
            "mlruns/exp_id/run_uuid/metrics/metric_key")

    def test_get_tags(self):
        # given
        exp = MagicMock()
        exp.name = 'EXPeriMENT-NaMe'
        run = MagicMock()
        run.info = MagicMock()
        run.info.name = 'RuN-NAme'

        # then
        # pylint: disable=protected-access
        self.assertEqual(
            DataLoader._get_tags(exp, run),
            ['experiment-name', 'run-name'])

    def test_get_properties(self):
        # given
        Tag = namedtuple('Tag', 'key, value')
        exp = MagicMock()
        exp.experiment_id = 123
        exp.name = 'EXPeriMENT-NaMe'
        run = MagicMock()
        run.info = MagicMock()
        run.info.run_uuid = str(uuid.uuid4())
        run.info.name = 'Cool run name'
        run.data = MagicMock()
        run.data.tags = [Tag(key='key1', value='value1'), Tag(key='key2', value='value2')]

        # then
        # pylint: disable=protected-access
        self.assertEqual(
            DataLoader._get_properties(exp, run),
            {
                'mlflow/experiment/id': str(exp.experiment_id),
                'mlflow/experiment/name': exp.name,
                'mlflow/run/uuid': run.info.run_uuid,
                'mlflow/run/name': run.info.name,
                'key1': 'value1',
                'key2': 'value2'
            }
        )

    def test_get_params(self):
        # given
        Param = namedtuple('Param', 'key, value')
        run = MagicMock()
        run.data = MagicMock()
        run.data.params = [Param(key='key1', value='value1'), Param(key='key2', value='value2')]

        # then
        # pylint: disable=protected-access
        self.assertEqual(
            DataLoader._get_params(run),
            {
                'key1': 'value1',
                'key2': 'value2'
            }
        )
