from neptune_mlflow_plugin import create_neptune_tracking_uri


def test_create_plugin_uri():
    uri = create_neptune_tracking_uri()
    assert uri == "neptune-plugin://project=None"

    uri = create_neptune_tracking_uri(name="test_name")
    assert uri == "neptune-plugin://project=None/name=test_name"
