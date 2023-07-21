from __future__ import annotations

__all__ = ["NeptuneMlflowTracker"]

import os
from contextlib import contextmanager
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
    def inner(*args, **kwargs):
        tracking_uri = os.getenv("NEPTUNE_MLFLOW_URI")
        if not tracking_uri:
            return
        with preserve_tracking_uri():
            func(*args, **kwargs)
            mlflow.set_tracking_uri(tracking_uri)
            func(*args, **kwargs)

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


# import os
# from collections.abc import Mapping
# from typing import (
#     Any,
#     Optional,
#     Set,
#     Union,
# )
#
# import mlflow
# from mlflow import ActiveRun
# from mlflow.entities import (
#     Experiment,
#     Run,
# )
# from neptune import Run as NeptuneRun
# from neptune.handler import Handler
#
#
# def _to_neptune_tags(tags: Mapping[str, Any]) -> Set[Any]:
#     neptune_tags = set()
#     for _, v in tags.items():
#         neptune_tags.add(v)
#
#     return neptune_tags
#
#
# class MlflowPlugin:
#     def __init__(
#         self,
#         *,
#         api_token: Optional[str] = None,
#         project: Optional[str] = None,
#         base_namespace: str = "mlflow",
#     ) -> None:
#         self.api_token = api_token
#         self.project = project
#         self._neptune_run: Optional[NeptuneRun] = None
#         self._base_handler: Optional[Handler] = None
#
#         self._base_namespace = base_namespace
#         self._mlflow_client = mlflow.tracking.MlflowClient()
#
#     def set_tracking_uri(self, uri: Union[str, os.PathLike]) -> None:
#         if self._base_handler:
#             self._base_handler["tracking_uri"] = uri
#         return mlflow.set_tracking_uri(uri)
#
#     @staticmethod
#     def get_tracking_uri() -> str:
#         return mlflow.get_tracking_uri()
#
#     def create_experiment(
#         self, name: str, artifact_location: Optional[str] = None, tags: Optional[Mapping[str, Any]] = None
#     ) -> str:
#         experiment_id = mlflow.create_experiment(name, artifact_location, tags)
#         if self._base_handler:
#             neptune_tags = _to_neptune_tags(tags)
#             self._base_handler["experiment/tags"].add(neptune_tags)
#
#             self._base_handler["experiment/name"] = name
#             self._base_handler["experiment/experiment_id"] = experiment_id
#
#             experiment = self._mlflow_client.get_experiment(experiment_id)
#             self._base_handler["experiment/creation_time"] = experiment.creation_time
#             self._base_handler["experiment/last_update_time"] = experiment.last_update_time
#
#         return experiment_id
#
#     def set_experiment(self, experiment_name: Optional[str] = None, experiment_id: Optional[str] = None)
#     -> Experiment:
#         mlflow_experiment = mlflow.set_experiment(experiment_name, experiment_id)
#
#         if (
#             not self._neptune_run.exists(f"{self._base_namespace}/experiment")
#             or self._base_handler["experiment/experiment_id"].fetch() != experiment_id
#         ):
#
#             self._base_handler["experiment/tags"].add(_to_neptune_tags(mlflow_experiment.tags))
#             self._base_handler["experiment/name"] = experiment_name
#             self._base_handler["experiment/experiment_id"] = experiment_id
#             self._base_handler["experiment/creation_time"] = mlflow_experiment.creation_time
#             self._base_handler["experiment/last_update_time"] = mlflow_experiment.last_update_time
#
#         return mlflow_experiment
#
#     def start_run(
#         self,
#         run_id: Optional[str] = None,
#         experiment_id: Optional[str] = None,
#         run_name: Optional[str] = None,
#         nested: bool = False,
#         tags: Optional[Mapping[str, Any]] = None,
#         description: Optional[str] = None,
#     ) -> ActiveRun:
#         mlflow_run = mlflow.start_run(run_id, experiment_id, run_name, nested, tags, description)
#
#         if tags:
#             neptune_tags = _to_neptune_tags(tags)
#             self._base_handler[f"run/{run_id}/tags"].add(neptune_tags)
#
#         self._base_handler[f"run/{run_id}/status"] = mlflow_run.info.status
#         return mlflow_run
#
#     def end_run(self, status: str = "FINISHED") -> None:
#         run_id = mlflow.active_run().info.run_id
#         mlflow.end_run(status)
#         if self._neptune_run.exists(f"{self._base_namespace}/run/{run_id}"):
#             self._base_handler[f"run/{run_id}/status"] = status
#
#     @staticmethod
#     def active_run() -> Optional[ActiveRun]:
#         return mlflow.active_run()
#
#     @staticmethod
#     def last_active_run() -> Optional[Run]:
#         return mlflow.last_active_run()
#
#     def log_param(self, key: str, value: Any) -> Any:
#         ...
#
#     def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
#         ...
#
#     def set_tag(self, key: str, value: Any) -> None:
#         ...
#
#     def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
#         ...
#
#     def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None) -> None:
#         ...
#
#     def get_artifact_uri(self, artifact_path: Optional[str] = None) -> str:
#         ...
