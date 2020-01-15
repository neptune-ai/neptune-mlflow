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
import random

from click.testing import CliRunner

from neptune_mlflow_plugin import sync


class TestPlugin(unittest.TestCase):
    runner = CliRunner()

    def test_path_not_exist(self):
        path = '/tmp/{}'.format(random.randint(10000, 1000000))
        result = self.runner.invoke(sync, [path])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output.strip(), "ERROR: Directory `{}` doesn't exist".format(path))

    def test_path_is_not_dir(self):
        path = '/tmp/{}'.format(random.randint(10000, 1000000))
        with open(path, 'a') as f:
            f.write("text")
        result = self.runner.invoke(sync, [path])
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.output.strip(), "ERROR: `{}` is not a directory".format(path))
