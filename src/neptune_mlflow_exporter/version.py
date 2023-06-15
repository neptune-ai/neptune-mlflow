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

__all__ = ["__version__"]

import sys
from importlib.util import find_spec

if sys.version_info >= (3, 8):
    from importlib.metadata import (
        PackageNotFoundError,
        version,
    )
else:
    from importlib_metadata import (
        PackageNotFoundError,
        version,
    )

if not (find_spec("neptune") or find_spec("neptune-client")):
    msg = """
            The Neptune client library was not found.

            Install the neptune package with
                `pip install neptune`

            Need help? -> https://docs.neptune.ai/setup/installation/"""
    raise PackageNotFoundError(msg)

try:
    __version__ = version("neptune-mlflow")
except PackageNotFoundError:
    # package is not installed
    pass
