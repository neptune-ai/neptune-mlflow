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
    "encode_config",
    "decode_config",
    "get_login",
    "check_if_path_is_fileset",
]

import base64
import json
import os
import warnings
from pathlib import Path
from typing import (
    Any,
    Dict,
)
from urllib.parse import (
    urlparse,
    urlunsplit,
)

from neptune import Run
from neptune.attributes import FileSet

PLUGIN_SCHEME = "neptune"
DEFAULT_LOGIN = "runner"
DEFAULT_HOST = "track"


def encode_config(config: Dict[str, Any]) -> str:
    """
    Encodes configuration in the form of a dictionary into a string using base64.
    Args:
        config: dictionary to encode

    Returns:
        encoded configuration in the string form
    """
    config_str = json.dumps(config)

    path = base64.b64encode(config_str.encode("utf-8")).decode("utf-8")

    components = (PLUGIN_SCHEME, DEFAULT_HOST, path, "", "")

    return urlunsplit(components)


def decode_config(uri: str) -> Dict[str, Any]:
    """
    Decodes configuration from string URI
    Args:
        uri: URI that encodes configuration

    Returns:
        decoded configuration in a dictionary form
    """
    uri_parsed = urlparse(uri)

    config_str = uri_parsed.path.replace("/", "")

    return json.loads(base64.b64decode(config_str).decode("utf-8"))


def parse_neptune_kwargs_from_uri(uri: str) -> Dict[str, Any]:
    neptune_kwargs = decode_config(uri)

    if "custom_run_id" in neptune_kwargs:
        val = neptune_kwargs.pop("custom_run_id")
        warnings.warn(f"Passed custom_run_id '{val}' will be ignored.")

    if "with_id" in neptune_kwargs:
        val = neptune_kwargs.pop("with_id")
        warnings.warn(f"Passed run id '{val}' will be ignored.")

    return neptune_kwargs


def get_login() -> str:
    try:
        return os.getlogin()
    except OSError:
        # e.g. in CI
        return DEFAULT_LOGIN


def check_if_path_is_fileset(neptune_run: Run, path: str) -> bool:
    path_parts = Path(path).parts

    structure = neptune_run.get_structure()

    final_structure = structure
    for part in path_parts:
        final_structure = final_structure[part]
    return isinstance(final_structure, FileSet)
