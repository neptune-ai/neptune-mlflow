from neptune_mlflow_plugin import create_neptune_tracking_uri


def test_create_plugin_uri():
    uri = create_neptune_tracking_uri()
    assert uri.startswith("neptune")
