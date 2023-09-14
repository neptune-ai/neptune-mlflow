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

import os
import uuid
import zipfile
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import (
    List,
    Optional,
)

from mlflow.entities import (
    DatasetInput,
    Experiment,
    FileInfo,
    LifecycleStage,
    Metric,
    Param,
)
from mlflow.entities import Run as MlflowRun
from mlflow.entities import (
    RunData,
    RunInfo,
    RunStatus,
    ViewType,
)
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from mlflow.store.tracking import SEARCH_MAX_RESULTS_DEFAULT
from mlflow.store.tracking.abstract_store import AbstractStore
from mlflow.utils.file_utils import local_file_uri_to_path
from neptune import Run

from neptune_mlflow_plugin.impl.utils import (
    check_if_path_is_fileset,
    encode_config,
    get_login,
    parse_neptune_kwargs_from_uri,
)


class NeptuneTrackingStore(AbstractStore):
    def __init__(self, store_uri: Optional[str], artifact_uri: Optional[str]):
        self.store_uri = store_uri
        self.artifact_uri = artifact_uri

        self._neptune_kwargs = parse_neptune_kwargs_from_uri(store_uri)

        self._neptune_run: Optional[Run] = None

        self._current_run_id: Optional[str] = None

        super().__init__()

        self._login = get_login()

    def _del_neptune_run_if_exists(self) -> None:
        if not self._neptune_run:
            # run either not created or already deleted
            return

        self._neptune_run.sync()
        self._neptune_run.stop()
        self._neptune_run = None

    def get_neptune_run(self, run_id: str) -> Run:
        if self._neptune_run and self._current_run_id != run_id:
            self._del_neptune_run_if_exists()

        if not self._neptune_run:
            self._current_run_id = run_id
            self._neptune_run = Run(custom_run_id=run_id, **self._neptune_kwargs)

        return self._neptune_run

    def search_experiments(
        self,
        view_type=ViewType.ACTIVE_ONLY,
        max_results=SEARCH_MAX_RESULTS_DEFAULT,
        filter_string=None,
        order_by=None,
        page_token=None,
    ):
        pass

    def create_experiment(self, name, artifact_location, tags):
        return Experiment(
            experiment_id="neptune-mock-experiment",
            name=name,
            artifact_location=artifact_location,
            tags=tags,
            lifecycle_stage=LifecycleStage.ACTIVE,
            creation_time=datetime.now(),
            last_update_time=datetime.now(),
        )

    def get_experiment(self, experiment_id):
        return Experiment(
            experiment_id=experiment_id,
            name="neptune-mock-experiment",
            artifact_location="",
            lifecycle_stage=LifecycleStage.ACTIVE,
            creation_time=datetime.now(),
            last_update_time=datetime.now(),
        )

    def delete_experiment(self, experiment_id):
        pass

    def restore_experiment(self, experiment_id):
        pass

    def rename_experiment(self, experiment_id, new_name):
        pass

    def get_run(self, run_id):
        if self._neptune_run and run_id != self._current_run_id:
            self._neptune_run.sync()
            self._neptune_run.stop()
            self._current_run_id = run_id
            self._neptune_run = Run(custom_run_id=run_id, **self._neptune_kwargs)
        config = deepcopy(self._neptune_kwargs)

        # inject run ID to store URI
        config["run_id"] = run_id
        store_uri = encode_config(config)

        return MlflowRun(
            run_info=RunInfo(
                run_uuid=uuid.uuid4(),
                start_time=datetime.now(),
                end_time=None,
                experiment_id="mock_exp_id",
                user_id=self._login,
                lifecycle_stage=LifecycleStage.ACTIVE,
                status="running",
                run_id=run_id,
                artifact_uri=store_uri,
            ),
            run_data=RunData(),
        )

    def update_run_info(self, run_id, run_status, end_time, run_name):
        if run_status not in (RunStatus.FAILED, RunStatus.KILLED, RunStatus.FINISHED):
            return
        if not self._neptune_run:
            return

        self._del_neptune_run_if_exists()

    def create_run(self, experiment_id, user_id, start_time, tags, run_name):
        run = MlflowRun(
            run_info=RunInfo(
                run_uuid=str(uuid.uuid4()),
                start_time=start_time,
                end_time=None,
                experiment_id=experiment_id,
                user_id=self._login,
                lifecycle_stage=LifecycleStage.ACTIVE,
                status="running",
                artifact_uri=self.store_uri,
                run_name=run_name,
            ),
            run_data=RunData(),
        )

        self._del_neptune_run_if_exists()

        self._current_run_id = run.info.run_id
        self._neptune_run = Run(custom_run_id=run.info.run_id, **self._neptune_kwargs)
        return run

    def delete_run(self, run_id):
        pass

    def restore_run(self, run_id):
        pass

    def get_metric_history(self, run_id, metric_key, max_results=None, page_token=None):
        pass

    def _search_runs(self, experiment_ids, filter_string, run_view_type, max_results, order_by, page_token):
        pass

    def log_batch(self, run_id, metrics, params, tags):
        neptune_run = self.get_neptune_run(run_id)
        for metric in metrics:
            neptune_run[f"metrics/{metric.key}"].append(metric.value, step=metric.step, timestamp=metric.timestamp)

        neptune_run["params"].append({param.key: param.value for param in params})

    def log_inputs(self, run_id: str, datasets: Optional[List[DatasetInput]] = None):
        pass

    def record_logged_model(self, run_id, mlflow_model):
        pass

    def log_metric(self, run_id, metric: Metric):
        neptune_run = self.get_neptune_run(run_id)
        neptune_run[metric.key].append(metric.value, step=metric.step, timestamp=metric.timestamp / 1e3)

    def log_param(self, run_id, param: Param):
        neptune_run = self.get_neptune_run(run_id)
        neptune_run[param.key] = param.value

    def set_tag(self, run_id, tag):
        if tag.key:
            neptune_tags = [tag.key, tag.value]
        else:
            neptune_tags = tag.value

        neptune_run = self.get_neptune_run(run_id)
        neptune_run["sys/tags"].add(neptune_tags)


class NeptuneArtifactRepo(ArtifactRepository):
    def __init__(self, *args, **kwargs):
        super(NeptuneArtifactRepo, self).__init__(*args, **kwargs)
        self._artifact_dir = local_file_uri_to_path(self.artifact_uri)
        self._neptune_kwargs = parse_neptune_kwargs_from_uri(self.artifact_uri)
        self._run_id = self._neptune_kwargs.pop("run_id")

        # artifact-related run instances do not need to report those
        self._neptune_kwargs.update(
            {
                "capture_stderr": False,
                "capture_stdout": False,
                "capture_hardware_metrics": False,
            }
        )

        self._neptune_run: Optional[Run] = None

    @property
    def neptune_run(self) -> Run:
        if not self._neptune_run:
            self._neptune_run = Run(custom_run_id=self._run_id, **self._neptune_kwargs)

        return self._neptune_run

    def log_artifact(self, local_file, artifact_path=None):
        target_path = artifact_path if artifact_path else Path(local_file).stem

        self.neptune_run[target_path].upload(local_file, wait=True)

    def log_artifacts(self, local_dir, artifact_path=None):
        target_path = artifact_path if artifact_path else Path(local_dir).stem

        self.neptune_run[target_path].upload_files(os.path.join(local_dir, "*"), wait=True)

    def list_artifacts(self, path):
        return [
            FileInfo(path=entry.name, is_dir=(entry.file_type == "directory"), file_size=entry.size)
            for entry in self.neptune_run[path].list_fileset_files()
        ]

    def download_artifacts(self, artifact_path, dst_path=None):
        self.neptune_run[artifact_path].download(destination=dst_path)

        is_fileset = check_if_path_is_fileset(self.neptune_run, artifact_path)

        if is_fileset:
            if dst_path:
                local_path = os.path.join(dst_path, Path(artifact_path).stem + ".zip")
            else:
                local_path = artifact_path

            with zipfile.ZipFile(local_path) as zipped:
                zipped.extractall(dst_path)

            os.remove(local_path)

    def _download_file(self, remote_file_path, local_path):
        ...
