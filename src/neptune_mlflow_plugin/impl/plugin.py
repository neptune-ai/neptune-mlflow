import os
import uuid
import warnings
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

from mlflow.entities import (
    DatasetInput,
    LifecycleStage,
    Metric,
    Param,
)
from mlflow.entities import Run as MlflowRun
from mlflow.entities import (
    RunData,
    RunInfo,
    ViewType,
)
from mlflow.store.artifact.artifact_repo import ArtifactRepository
from mlflow.store.tracking import SEARCH_MAX_RESULTS_DEFAULT
from mlflow.store.tracking.abstract_store import AbstractStore
from mlflow.utils.file_utils import local_file_uri_to_path
from neptune import Run


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class RunProvider:
    def __init__(self, neptune_kwargs: Dict[str, Any]):
        self._neptune_kwargs = neptune_kwargs
        self._mlflow_run_id = None

        self._neptune_run: Optional[Run] = None

    def set_mlflow_run_id(self, run_id) -> None:
        self._mlflow_run_id = run_id

    @property
    def mlflow_run_id(self) -> str:
        return self._mlflow_run_id

    def get_or_create_neptune_run(self, run_id: str) -> Run:
        if self._neptune_run:
            if self._neptune_run["sys/custom_run_id"].fetch() == run_id:
                return self._neptune_run
            else:  # new mlflow run
                self._neptune_run.sync()
                self._neptune_run.stop()

        # if reached here, there is no active neptune run
        self._neptune_run = Run(custom_run_id=run_id, **self._neptune_kwargs)
        return self._neptune_run


def parse_neptune_kwargs_from_uri(uri: str) -> Dict[str, Any]:
    neptune_kwargs = {}

    uri_split = uri.split("://")
    assert len(uri_split) == 2

    init_args = uri_split[1]  # first argument will be a scheme e.g. 'neptune-plugin'

    init_args = init_args.split("/")

    for arg in init_args:

        # empty string
        if not arg:
            continue

        key, val = arg.split("=")

        # disregard passed custom_run_id
        if key == "custom_run_id":
            warnings.warn(f"Passed custom_run_id '{val}' will be ignored.")
            continue

        # convert string booleans to booleans
        if val in {"True", "False"}:
            val = val != "False"

        if val == "None":
            val = None

        neptune_kwargs[key] = val

    return neptune_kwargs


class NeptuneTrackingStore(AbstractStore):
    def __init__(self, store_uri: Optional[str], artifact_uri: Optional[str]):
        self.store_uri = store_uri
        self.artifact_uri = artifact_uri

        self._neptune_kwargs = parse_neptune_kwargs_from_uri(store_uri)

        self._run_provider = RunProvider(self._neptune_kwargs)

        self._api_token = self._neptune_kwargs.pop("api_token", None)
        self._project = self._neptune_kwargs.pop("project", None)

        self._neptune_run: Optional[Run] = None

        super().__init__()

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
        ...

    def get_experiment(self, experiment_id):
        pass

    def delete_experiment(self, experiment_id):
        pass

    def restore_experiment(self, experiment_id):
        pass

    def rename_experiment(self, experiment_id, new_name):
        pass

    def get_run(self, run_id):
        return MlflowRun(
            run_info=RunInfo(
                run_uuid=uuid.uuid4(),
                start_time=datetime.now(),
                end_time=None,
                experiment_id="mock_exp_id",
                user_id=os.getlogin(),
                lifecycle_stage=LifecycleStage.ACTIVE,
                status="running",
                run_id=run_id,
                artifact_uri=self.store_uri,
            ),
            run_data=RunData(),
        )

    def update_run_info(self, run_id, run_status, end_time, run_name):
        ...

    def create_run(self, experiment_id, user_id, start_time, tags, run_name):
        run = MlflowRun(
            run_info=RunInfo(
                run_uuid=str(uuid.uuid4()),
                start_time=start_time,
                end_time=None,
                experiment_id=experiment_id,
                user_id=os.getlogin(),
                lifecycle_stage=LifecycleStage.ACTIVE,
                status="running",
                artifact_uri=self.store_uri,
                run_name=run_name,
            ),
            run_data=RunData(),
        )

        self._run_provider.set_mlflow_run_id(run.info.run_id)

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
        self._neptune_run = self._run_provider.get_or_create_neptune_run(self._run_provider.mlflow_run_id)

        for metric in metrics:
            self._neptune_run[f"metrics/{metric.key}"].append(
                metric.value, step=metric.step, timestamp=metric.timestamp
            )

        for param in params:
            self._neptune_run[f"params/{param.key}"].append(param.value)

    def log_inputs(self, run_id: str, datasets: Optional[List[DatasetInput]] = None):
        pass

    def record_logged_model(self, run_id, mlflow_model):
        pass

    def log_metric(self, run_id, metric: Metric):
        self._neptune_run = self._run_provider.get_or_create_neptune_run(self._run_provider.mlflow_run_id)

        self._neptune_run[metric.key].append(metric.value, step=metric.step, timestamp=metric.timestamp / 1e3)

    def log_param(self, run_id, param: Param):
        self._neptune_run = self._run_provider.get_or_create_neptune_run(self._run_provider.mlflow_run_id)

        self._neptune_run[param.key] = param.value

    def set_tag(self, run_id, tag):
        self._neptune_run = self._run_provider.get_or_create_neptune_run(self._run_provider.mlflow_run_id)

        if tag.key:
            neptune_tags = [tag.key, tag.value]
        else:
            neptune_tags = tag.value

        self._neptune_run["sys/tags"].add(neptune_tags)


class NeptuneArtifactRepo(ArtifactRepository):
    def __init__(self, *args, **kwargs):
        super(NeptuneArtifactRepo, self).__init__(*args, **kwargs)
        self._artifact_dir = local_file_uri_to_path(self.artifact_uri)
        self._neptune_kwargs = parse_neptune_kwargs_from_uri(self.artifact_uri)

        self._run_provider = RunProvider(self._neptune_kwargs)

        self._api_token = self._neptune_kwargs.pop("api_token", None)
        self._project = self._neptune_kwargs.pop("project", None)

        self._neptune_run: Optional[Run] = None

    def log_artifact(self, local_file, artifact_path=None):
        self._neptune_run = self._run_provider.get_or_create_neptune_run(self._run_provider.mlflow_run_id)

        target_path = artifact_path if artifact_path else Path(local_file).stem

        self._neptune_run[target_path].upload(local_file)

        self._neptune_run.sync()

    def log_artifacts(self, local_dir, artifact_path=None):
        self._neptune_run = self._run_provider.get_or_create_neptune_run(self._run_provider.mlflow_run_id)

        target_path = artifact_path if artifact_path else Path(local_dir).stem

        self._neptune_run[target_path].upload_files(os.path.join(local_dir, "*"))

        self._neptune_run.sync()

    def list_artifacts(self, path):
        pass

    def _download_file(self, remote_file_path, local_path):
        pass
