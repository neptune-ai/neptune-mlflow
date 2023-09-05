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

__all__ = ["create_neptune_tracking_uri"]

from typing import Optional
from urllib.parse import urlunsplit

PLUGIN_SCHEME = "neptune-plugin"


def create_neptune_tracking_uri(project: Optional[str] = None, **kwargs) -> str:
    path = "/".join([f"{key}={value}" for key, value in kwargs.items()])

    components = (PLUGIN_SCHEME, f"project={project}", path, "", "")
    return urlunsplit(components)
