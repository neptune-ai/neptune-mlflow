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

__all__ = [
    "parse_neptune_kwargs_from_uri",
]

import base64
import json
import warnings
from typing import (
    Any,
    Dict,
)
from urllib.parse import urlparse


def parse_neptune_kwargs_from_uri(uri: str) -> Dict[str, Any]:
    uri_parsed = urlparse(uri)

    kwarg_str = uri_parsed.path.replace("/", "")

    neptune_kwargs: Dict = json.loads(base64.b64decode(kwarg_str).decode("utf-8"))

    if "custom_run_id" in neptune_kwargs:
        val = neptune_kwargs.pop("custom_run_id")
        warnings.warn(f"Passed custom_run_id '{val}' will be ignored.")

    if "with_id" in neptune_kwargs:
        val = neptune_kwargs.pop("with_id")
        warnings.warn(f"Passed run id '{val}' will be ignored.")

    return neptune_kwargs
