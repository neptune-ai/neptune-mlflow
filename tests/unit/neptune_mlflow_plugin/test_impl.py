from neptune_mlflow_plugin import create_neptune_tracking_uri


def test_create_plugin_uri():
    uri = create_neptune_tracking_uri()
    assert uri == "neptune-plugin://api_token=None/project=None/mode=async/name=Untitled/capture_stdout=True"

    uri = create_neptune_tracking_uri(name="test_name")
    assert uri == "neptune-plugin://api_token=None/project=None/mode=async/name=test_name/capture_stdout=True"
