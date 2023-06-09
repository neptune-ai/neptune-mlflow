import os
from collections.abc import Mapping
from typing import (
    Any,
    Optional,
    Union,
)

import mlflow
from mlflow import ActiveRun
from mlflow.entities import (
    Experiment,
    Run,
)
from neptune import Run as NeptuneRun
from neptune import init_run
from neptune.handler import Handler


class MlflowPlugin:
    def __init__(
        self,
        neptune_run: Optional[Union[NeptuneRun, Handler]] = None,
        *,
        api_token: Optional[str] = None,
        project: Optional[str] = None,
        base_namespace: str = "mlflow",
    ) -> None:
        self._neptune_run = neptune_run

        if not self._neptune_run:
            self._neptune_run = init_run(
                api_token=api_token,
                project=project,
            )

        self._base_handler = self._neptune_run[base_namespace]
        self._mlflow_client = mlflow.tracking.MlflowClient()

    def set_tracking_uri(self, uri: Union[str, os.PathLike]) -> None:
        self._base_handler["tracking_uri"] = uri
        return mlflow.set_tracking_uri(uri)

    @staticmethod
    def get_tracking_uri() -> str:
        return mlflow.get_tracking_uri()

    def create_experiment(
        self, name: str, artifact_location: Optional[str] = None, tags: Optional[Mapping[str, Any]] = None
    ) -> str:
        neptune_tags = set()
        for _, v in tags.items():
            neptune_tags.add(v)

        self._base_handler["experiment/name"] = name

        experiment_id = mlflow.create_experiment(name, artifact_location, tags)
        self._base_handler["experiment/experiment_id"] = experiment_id

        experiment = self._mlflow_client.get_experiment(experiment_id)
        self._base_handler["experiment/creation_time"] = experiment.creation_time
        self._base_handler["experiment/last_update_time"] = experiment.last_update_time
        return experiment_id

    def set_experiment(self, experiment_name: Optional[str] = None, experiment_id: Optional[str] = None) -> Experiment:
        ...

    def start_run(
        self,
        run_id: Optional[str] = None,
        experiment_id: Optional[str] = None,
        run_name: Optional[str] = None,
        nested: bool = False,
        tags: Optional[Mapping[str, Any]] = None,
        description: Optional[str] = None,
    ) -> ActiveRun:
        ...

    def end_run(self, status: str = "FINISHED") -> None:
        ...

    def active_run(self) -> Optional[ActiveRun]:
        ...

    def last_active_run(self) -> Optional[Run]:
        ...

    def log_param(self, key: str, value: Any) -> Any:
        ...

    def log_metric(self, key: str, value: float, step: Optional[int] = None) -> None:
        ...

    def set_tag(self, key: str, value: Any) -> None:
        ...

    def log_artifact(self, local_path: str, artifact_path: Optional[str] = None) -> None:
        ...

    def log_artifacts(self, local_dir: str, artifact_path: Optional[str] = None) -> None:
        ...

    def get_artifact_uri(self, artifact_path: Optional[str] = None) -> str:
        ...
