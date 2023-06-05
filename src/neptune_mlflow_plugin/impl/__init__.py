import os
from collections.abc import Mapping
from typing import (
    Any,
    Optional,
    Union,
)

from mlflow import ActiveRun
from mlflow.entities import (
    Experiment,
    Run,
)


def set_tracking_uri(uri: Union[str, os.PathLike]) -> None:
    ...


def get_tracking_uri() -> str:
    ...


def create_experiment(
    name: str, artifact_location: Optional[str] = None, tags: Optional[Mapping[str, Any]] = None
) -> str:
    ...


def set_experiment(experiment_name: Optional[str] = None, experiment_id: Optional[str] = None) -> Experiment:
    ...


def start_run(
    run_id: Optional[str] = None,
    experiment_id: Optional[str] = None,
    run_name: Optional[str] = None,
    nested: bool = False,
    tags: Optional[Mapping[str, Any]] = None,
    description: Optional[str] = None,
) -> ActiveRun:
    ...


def end_run(status: str = "FINISHED") -> None:
    ...


def active_run() -> Optional[ActiveRun]:
    ...


def last_active_run() -> Optional[Run]:
    ...


def log_param(key: str, value: Any) -> Any:
    ...


def log_metric(key: str, value: float, step: Optional[int] = None) -> None:
    ...


def set_tag(key: str, value: Any) -> None:
    ...


def log_artifact(local_path: str, artifact_path: Optional[str] = None) -> None:
    ...


def log_artifacts(local_dir: str, artifact_path: Optional[str] = None) -> None:
    ...


def get_artifact_uri(artifact_path: Optional[str] = None) -> str:
    ...
