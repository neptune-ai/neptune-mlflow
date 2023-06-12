from unittest.mock import (
    MagicMock,
    patch,
)

from neptune import init_run

from neptune_mlflow_plugin import MlflowPlugin


@patch("neptune_mlflow_plugin.impl.init_run")
def test_plugin_instantiation(mock_init_run):
    MlflowPlugin(
        neptune_run=MagicMock(),
    )

    mock_init_run.assert_not_called()

    MlflowPlugin(
        api_token="some_token",
        project="some_project",
    )

    mock_init_run.assert_called_once_with(api_token="some_token", project="some_project")

    MlflowPlugin(base_namespace="test_namespace")
    assert mock_init_run.call_count == 2


def test_set_tracking_uri(mlflow: MlflowPlugin):
    uri = "some_tracking_uri"

    with patch("neptune_mlflow_plugin.impl.mlflow") as mock_mlflow:
        mlflow.set_tracking_uri(uri)

        assert mlflow._neptune_run["mlflow/tracking_uri"].fetch() == uri
        mock_mlflow.set_tracking_uri.assert_called_once_with(uri)


def test_get_tracking_uri(mlflow: MlflowPlugin):
    with patch("neptune_mlflow_plugin.impl.mlflow") as mock_mlflow:
        mlflow.get_tracking_uri()
        mock_mlflow.get_tracking_uri.assert_called_once()


def test_create_experiment(mlflow: MlflowPlugin, mock_experiment):
    with patch(
        "neptune_mlflow_plugin.impl.mlflow.tracking.MlflowClient.get_experiment", return_value=mock_experiment
    ) as mock_get_experiment:

        with patch("mlflow.create_experiment", return_value="test_id") as mock_create_experiment:
            experiment_id = mlflow.create_experiment(
                "test_experiment", artifact_location="some_location", tags={"tag1": "val1"}
            )
            mock_create_experiment.assert_called_once_with("test_experiment", "some_location", {"tag1": "val1"})
            mock_get_experiment.assert_called_once_with("test_id")

            assert experiment_id == "test_id"

            assert mlflow._neptune_run["mlflow/experiment/tags"].fetch() == {"val1"}
            assert mlflow._neptune_run["mlflow/experiment/name"].fetch() == "test_experiment"
            assert mlflow._neptune_run["mlflow/experiment/experiment_id"].fetch() == "test_id"
            assert mlflow._neptune_run["mlflow/experiment/creation_time"].fetch() == "some_creation_time"
            assert mlflow._neptune_run["mlflow/experiment/last_update_time"].fetch() == "some_update_time"


def test_set_experiment(mock_experiment):
    with init_run(mode="debug") as run:
        mlflow = MlflowPlugin(run)
        with patch("neptune_mlflow_plugin.impl.mlflow") as mock_mlflow:
            mock_mlflow.set_experiment.return_value = mock_experiment

            mlflow.set_experiment("test_experiment", "test_id")

            mock_mlflow.set_experiment.assert_called_once_with("test_experiment", "test_id")

            assert mlflow._neptune_run["mlflow/experiment/tags"].fetch() == {"val1"}
            assert mlflow._neptune_run["mlflow/experiment/name"].fetch() == "test_experiment"
            assert mlflow._neptune_run["mlflow/experiment/experiment_id"].fetch() == "test_id"
            assert mlflow._neptune_run["mlflow/experiment/creation_time"].fetch() == "some_creation_time"
            assert mlflow._neptune_run["mlflow/experiment/last_update_time"].fetch() == "some_update_time"


def test_start_run(mlflow: MlflowPlugin):
    mlflow_run = MagicMock()
    mlflow_run.info.status = "RUNNING"
    with patch("neptune_mlflow_plugin.impl.mlflow") as mock_mlflow:
        mock_mlflow.start_run.return_value = mlflow_run
        mlflow.start_run("test_run_id", "test_experiment_id", tags={"tag1": "val1"})
        mock_mlflow.start_run.assert_called_once_with(
            "test_run_id",
            "test_experiment_id",
            None,
            False,
            {"tag1": "val1"},
            None,
        )

        assert mlflow._neptune_run["mlflow/run/test_run_id/tags"].fetch() == {"val1"}
        assert mlflow._neptune_run["mlflow/run/test_run_id/status"].fetch() == "RUNNING"


def test_end_run(mlflow: MlflowPlugin):
    status = "TEST_STATUS_FINISHED"
    mlflow_run = MagicMock()
    mlflow_run.info.status = "RUNNING"
    mlflow_run.info.run_id = "test_run_id"

    with patch("neptune_mlflow_plugin.impl.mlflow") as mock_mlflow:
        mock_mlflow.start_run.return_value = mlflow_run
        mock_mlflow.active_run.return_value = mlflow_run
        mlflow.start_run("test_run_id", "test_experiment_id", tags={"tag1": "val1"})

        mlflow.end_run(status)

        mock_mlflow.end_run.assert_called_once_with(status)

        assert mlflow._neptune_run["mlflow/run/test_run_id/status"].fetch() == status


def test_active_run(mlflow: MlflowPlugin):
    with patch("neptune_mlflow_plugin.impl.mlflow") as mock_mlflow:
        mlflow.active_run()
        mock_mlflow.active_run.assert_called_once()


def test_last_active_run(mlflow: MlflowPlugin):
    with patch("neptune_mlflow_plugin.impl.mlflow") as mock_mlflow:
        mlflow.last_active_run()
        mock_mlflow.last_active_run.assert_called_once()
