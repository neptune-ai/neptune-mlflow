import uuid
import warnings
from datetime import datetime
from typing import (
    List,
    Optional,
)

import mlflow
from mlflow.entities import (
    DatasetInput,
    Metric,
    Param,
)
from mlflow.entities import Run as MlflowRun
from mlflow.entities import (
    RunData,
    RunInfo,
    ViewType,
)
from mlflow.entities.lifecycle_stage import LifecycleStage
from mlflow.store.tracking import SEARCH_MAX_RESULTS_DEFAULT
from mlflow.store.tracking.abstract_store import AbstractStore
from neptune import Run as NeptuneRun


class NeptuneTrackingStore(AbstractStore):
    def __init__(self, store_uri: Optional[str], artifact_uri: Optional[str]):
        self.store_uri = store_uri
        self.artifact_uri = artifact_uri
        _, init_args = store_uri.split("://")

        init_args = init_args.split("/")

        self._api_token = init_args[0] if init_args[0] else None
        self._project = init_args[1] if init_args[1] else None

        self._neptune_kwargs = {}

        if len(init_args) > 2:
            for init_arg in init_args[2:]:
                k, v = init_arg.split("=")
                self._neptune_kwargs[k] = v

        passed_custom_run_id = self._neptune_kwargs.pop("custom_run_id", None)
        if passed_custom_run_id:
            warnings.warn(f"Passed custom_run_id '{passed_custom_run_id}' will be ignored.")

        self._neptune_run: Optional[NeptuneRun] = None
        super().__init__()

    def _manage_neptune_run_creation(self, run_id: str) -> None:
        if self._neptune_run:
            if self._neptune_run["sys/custom_run_id"].fetch() != run_id:  # new mlflow run
                self._neptune_run.sync()
                self._neptune_run.stop()

            else:
                return

        # if reached here, there is no active neptune run
        self._neptune_run = NeptuneRun(
            api_token=self._api_token, project=self._project, custom_run_id=run_id, **self._neptune_kwargs
        )

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
        pass

    def update_run_info(self, run_id, run_status, end_time, run_name):
        pass

    def create_run(self, experiment_id, user_id, start_time, tags, run_name):
        run_info = RunInfo(
            uuid.uuid4(),
            experiment_id,
            user_id,
            mlflow.entities.run_status.RunStatus.RUNNING,
            datetime.now(),
            None,
            LifecycleStage.ACTIVE,
            run_name=run_name,
        )

        run_data = RunData()

        return MlflowRun(run_info, run_data)

    def delete_run(self, run_id):
        pass

    def restore_run(self, run_id):
        pass

    def get_metric_history(self, run_id, metric_key, max_results=None, page_token=None):
        pass

    def _search_runs(self, experiment_ids, filter_string, run_view_type, max_results, order_by, page_token):
        pass

    def log_batch(self, run_id, metrics, params, tags):
        pass

    def log_inputs(self, run_id: str, datasets: Optional[List[DatasetInput]] = None):
        pass

    def record_logged_model(self, run_id, mlflow_model):
        pass

    def log_metric(self, run_id, metric: Metric):
        self._manage_neptune_run_creation(run_id)

        self._neptune_run[metric.key].append(metric.value, step=metric.step, timestamp=metric.timestamp / 1e3)

    def log_param(self, run_id, param: Param):
        self._manage_neptune_run_creation(run_id)

        self._neptune_run[param.key] = param.value
