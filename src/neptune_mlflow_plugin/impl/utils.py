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
    "singleton",
    "parse_neptune_kwargs_from_uri",
]

import warnings
from typing import (
    Any,
    AnyStr,
    Dict,
    Set,
)
from urllib.parse import urlparse


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


def parse_neptune_kwargs_from_uri(uri: str) -> Dict[str, Any]:
    neptune_kwargs = {}

    uri_parsed = urlparse(uri)

    project_str = uri_parsed.netloc
    kwarg_str = uri_parsed.path

    project = project_str.split("=")[1]
    if project == "None":
        project = None

    neptune_kwargs["project"] = project

    for arg in kwarg_str.split("/"):

        # empty string
        if not arg:
            continue

        key, val = arg.split("=")

        # disregard passed custom_run_id
        if key == "custom_run_id":
            warnings.warn(f"Passed custom_run_id '{val}' will be ignored.")
            continue

        # disregard passed id
        if key == "with_id":
            warnings.warn(f"Passed run id '{val}' will be ignored.")
            continue

        # parse tags
        if key == "tags":
            val = _parse_tags(val)

        # convert string booleans to booleans
        if val in {"True", "False"}:
            val = val != "False"

        if val == "None":
            val = None

        if key == "flush_period":
            val = float(val)

        neptune_kwargs[key] = val

    return neptune_kwargs


def _parse_tags(tag_str: AnyStr) -> Set[AnyStr]:
    """
    Parse a string representation of tags
    Args:
        tag_str: string representation of tags in the URI
        Can be either a string representation of a single tag, or a list

    Returns:
        Set of tags
    """
    result = set()

    if tag_str[0] in ["[", "{"] and tag_str[-1] in ["]", "}"]:
        # parse a list or set of tags e.g. "['tag1', 'tag2']" or "{'tag1', 'tag2'}"
        tag_str = tag_str[1:-1]
        tags = tag_str.split(",")

    else:
        # single tag e.g. "'tag1'"
        tags = [tag_str]

    for tag in tags:
        tag = tag.replace("'", "").strip()  # "'tag1'" -> "tag1"
        result.add(tag)

    return result
