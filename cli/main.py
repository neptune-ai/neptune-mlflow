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

from neptune import Session

from cli.data_loader import DataLoader


@click.group()
def main():
    pass


@main.group('sync')
def sync():
    pass


@sync.command('mlflow')
@click.argument('path', required=False)
@click.option('--api-token', '-a', help='Neptune Authorization Token')
@click.option('--project', '-p', help='Project name')
def sync_mlflow_data(path, api_token, project):
    if path is None:
        path = "."
    if project is None:
        project = os.getenv('NEPTUNE_PROJECT')

    if not os.path.exists(path):
        click.echo("ERROR: Directory `{}` doesn't exist".format(path), err=True)
        sys.exit(1)

    if not os.path.isdir(path):
        click.echo("ERROR: `{}` is not a directory".format(path), err=True)
        sys.exit(1)

    session = Session(api_token)
    project = session.get_project(project)

    loader = DataLoader(project, path)
    loader.run()


if __name__ == '__main__':
    main()
