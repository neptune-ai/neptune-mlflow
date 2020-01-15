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

import click


@click.command('mlflow')
@click.argument('path', required=False)
@click.option('--project', '-p', help='Project name')
def sync(path, project):
    """Upload mlflow runs data to Neptune.
    PATH is a directory where Neptune will look for `mlruns` directory with mlflow data.

    Examples:

        neptune mlflow .

        neptune mlflow /path

        neptune mlflow /path --project username/sandbox

    """

    # We do not want to import anything if process was executed for autocompletion purposes.
    from neptune_mlflow.sync import sync as run_sync
    return run_sync(path=path, project=project)
