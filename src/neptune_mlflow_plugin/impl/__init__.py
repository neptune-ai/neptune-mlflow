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

import base64
import json
from typing import Optional
from urllib.parse import urlunsplit

PLUGIN_SCHEME = "neptune"


def create_neptune_tracking_uri(project: Optional[str] = None, **kwargs) -> str:
    if "tags" in kwargs and isinstance(kwargs["tags"], set):
        tags = [tag for tag in kwargs["tags"]]  # set object is not JSON serializable

        kwargs["tags"] = tags

    kwargs_str = json.dumps(kwargs)

    path = base64.b64encode(kwargs_str.encode("utf-8")).decode("utf-8")

    components = (PLUGIN_SCHEME, f"project={project}", path, "", "")

    return urlunsplit(components)
