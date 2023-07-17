import uuid
from datetime import datetime
from typing import Optional

import mlflow
from mlflow.entities import Metric
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
    def __init__(self, store_uri, artifact_uri):
        self.store_uri = store_uri
        self.artifact_uri = artifact_uri

        _, init_args = store_uri.split("//")

        init_args = init_args.split("/")

        self.api_token = init_args[0] if init_args[0] else None
        self.project = init_args[1] if init_args[1] else None

        self._neptune_run: Optional[NeptuneRun] = None

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

    def record_logged_model(self, run_id, mlflow_model):
        pass

    def log_metric(self, run_id, metric: Metric):
        self.log_batch(run_id, metrics=[metric], params=[], tags=[])

        if not self._neptune_run:
            self._neptune_run = NeptuneRun(api_token=self.api_token, project=self.project)

        self._neptune_run[metric.key].append(metric.value, step=metric.step, timestamp=metric.timestamp / 1e3)
