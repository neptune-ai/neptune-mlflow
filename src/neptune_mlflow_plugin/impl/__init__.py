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

import functools

import neptune

from neptune_mlflow_plugin.impl.utils import encode_config


@functools.wraps(neptune.init_run)
def create_neptune_tracking_uri(**kwargs) -> str:
    kwargs["tags"] = (
        list(kwargs["tags"]) if ("tags" in kwargs and isinstance(kwargs["tags"], set)) else kwargs.get("tags")
    )

    return encode_config(kwargs)
