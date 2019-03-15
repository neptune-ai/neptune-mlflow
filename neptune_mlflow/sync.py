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

import os
import sys

import click

import neptune
from neptune_mlflow.data_loader import DataLoader


def sync(path, project):
    if path is None:
        path = "."

    if not os.path.exists(path):
        click.echo("ERROR: Directory `{}` doesn't exist".format(path), err=True)
        sys.exit(1)

    if not os.path.isdir(path):
        click.echo("ERROR: `{}` is not a directory".format(path), err=True)
        sys.exit(1)

    if not os.path.exists(os.path.join(path, "mlruns")):
        click.echo("ERROR: No 'mlruns' directory in {}".format(path), err=True)
        sys.exit(1)

    project = neptune.init(project_qualified_name=project)

    loader = DataLoader(project, path)
    loader.run()
