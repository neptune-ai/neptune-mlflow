from neptune_mlflow_plugin import create_neptune_tracking_uri


def test_create_plugin_uri():
    uri = create_neptune_tracking_uri()
    assert uri == (
        "neptune-plugin://api_token=None/project=None/mode=async/name=Untitled/description=/capture_stdout"
        "=True/capture_stderr=True/capture_hardware_metrics=True/fail_on_exception=True"
        "/monitoring_namespace=monitoring/flush_period=5/capture_traceback=True"
    )

    uri = create_neptune_tracking_uri(name="test_name")
    assert uri == (
        "neptune-plugin://api_token=None/project=None/mode=async/name=test_name/description=/capture_stdout"
        "=True/capture_stderr=True/capture_hardware_metrics=True/fail_on_exception=True"
        "/monitoring_namespace=monitoring/flush_period=5/capture_traceback=True"
    )
