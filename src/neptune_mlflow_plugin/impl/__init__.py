from __future__ import annotations

__all__ = ["NeptuneMlflowTracker"]

import os
from contextlib import contextmanager
from functools import wraps
from threading import Thread
from typing import (
    TYPE_CHECKING,
    Any,
)

import mlflow

if TYPE_CHECKING:
    from mlflow import ActiveRun


@contextmanager
def preserve_tracking_uri():
    tracking_uri = mlflow.get_tracking_uri()
    yield
    mlflow.set_tracking_uri(tracking_uri)


def log_both(func):
    @wraps(func)
    def inner(*args, **kwargs):
        mlflow_tracking_uri = mlflow.get_tracking_uri()
        neptune_tracking_uri = os.getenv("NEPTUNE_MLFLOW_URI")
        if not neptune_tracking_uri:
            return

        def log(tracking_uri, *args, **kwargs):
            mlflow.set_tracking_uri(tracking_uri)
            func(*args, **kwargs)

        t1 = Thread(target=log, args=(mlflow_tracking_uri, *args), kwargs=kwargs)
        t2 = Thread(target=log, args=(neptune_tracking_uri, *args), kwargs=kwargs)

        with preserve_tracking_uri():
            t1.start()
            t2.start()

            t1.join()
            t2.join()

    return inner


class NeptuneMlflowTracker:
    PLUGIN_SCHEME = "neptune-plugin"

    def __init__(self, api_token=None, project=None, **kwargs):
        self.api_token = api_token if api_token else ""
        self.project = project if project else ""

        self.neptune_plugin_uri = f"{NeptuneMlflowTracker.PLUGIN_SCHEME}://{self.api_token}/{self.project}"

        if kwargs:
            other_args = "/" + "/".join([f"{key}={val}" for key, val in kwargs.items()])

            self.neptune_plugin_uri += other_args

        os.environ["NEPTUNE_MLFLOW_URI"] = self.neptune_plugin_uri

    @log_both
    def log_metric(self, key, value, step=None):
        mlflow.log_metric(key, value, step=step)

    @log_both
    def log_param(self, key, value):
        mlflow.log_param(key, value)

    @log_both
    def set_tag(self, key, value):
        mlflow.set_tag(key, value)

    @log_both
    def log_artifact(self, local_path, run_id: str):
        os.environ["NEPTUNE_MLFLOW_RUN_ID"] = run_id
        mlflow.log_artifact(local_path)

    @log_both
    def log_metrics(self, metrics, step):
        mlflow.log_metrics(metrics, step)

    @log_both
    def log_params(self, params):
        mlflow.log_params(params)

    def start_run(
        self,
        run_id: str | None = None,
        experiment_id: str | None = None,
        run_name: str | None = None,
        nested: bool = False,
        tags: dict[str, Any] | None = None,
        description: str | None = None,
    ) -> "ActiveRun":
        run = mlflow.start_run(run_id, experiment_id, run_name, nested, tags, description)
        experiment_id = run.info.experiment_id
        experiment_name = mlflow.get_experiment(experiment_id).name

        with preserve_tracking_uri():
            mlflow.set_tracking_uri(self.neptune_plugin_uri)
            mlflow.set_tag("", f"[EXP NAME] {experiment_name}")
            mlflow.set_tag("", f"[RUN ID] {run.info.run_id}")
            mlflow.set_tag("", f"[RUN NAME] {run.info.run_name}")

        return run
