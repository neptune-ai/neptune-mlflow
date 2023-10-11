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
    """Sets up a Neptune tracking URI for logging MLflow experiment metadata.

    This lets you direct your metadata to Neptune instead of MLflow, without needing to change your MLflow logging code.

    The function wraps neptune.init_run(), so you have the same parameters available for customizing your run or
    limiting what is logged. The exceptions are with_id and custom_run_id, which will be ignored if provided (as calling
    this function always creates a new Neptune run).
    For the full list, see the Neptune documentation: https://docs.neptune.ai/api/neptune/#init_run

    Examples:
        Create default Neptune tracking URI:
        >>> from neptune_mlflow_plugin import create_neptune_tracking_uri
        >>> uri = create_neptune_tracking_uri()
        >>> mlflow.set_tracking_uri(uri)
        >>> with mlflow.start_run() as mlflow_run:
        ...     ...

        Create Neptune run with more customized options:
        >>> uri = create_neptune_tracking_uri(
        ...     name="my-custom-run-name",
        ...     description="Description of the run",
        ...     tags=["test", "mlflow"],
        ...     source_files="**/.py",
        ...     dependencies="infer",
        ... )

    For detailed instructions, see the Neptune-MLflow integration guide: https://docs.neptune.ai/integrations/mlflow/
    """
    kwargs["tags"] = (
        list(kwargs["tags"]) if ("tags" in kwargs and isinstance(kwargs["tags"], set)) else kwargs.get("tags")
    )

    return encode_config(kwargs)
