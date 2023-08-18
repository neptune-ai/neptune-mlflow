from __future__ import annotations

__all__ = ["create_neptune_tracking_uri"]

from typing import Optional

PLUGIN_SCHEME = "neptune-plugin"


def create_neptune_tracking_uri(
    *,
    api_token: Optional[str] = None,
    project: Optional[str] = None,
    mode: str = "async",
    name: str = "Untitled",
    description: str = "",
    capture_stdout: bool = True,
    capture_stderr: bool = True,
    capture_hardware_metrics: bool = True,
    fail_on_exception: bool = True,
    monitoring_namespace: str = "monitoring",
    flush_period: float = 5,
    capture_traceback: bool = True,
) -> str:
    return (
        f"{PLUGIN_SCHEME}://"
        f"api_token={api_token}/"
        f"project={project}/"
        f"mode={mode}/"
        f"name={name}/"
        f"description={description}/"
        f"capture_stdout={capture_stdout}/"
        f"capture_stderr={capture_stderr}/"
        f"capture_hardware_metrics={capture_hardware_metrics}/"
        f"fail_on_exception={fail_on_exception}/"
        f"monitoring_namespace={monitoring_namespace}/"
        f"flush_period={flush_period}/"
        f"capture_traceback={capture_traceback}"
    )
