from datetime import datetime
from unittest.mock import (
    MagicMock,
    patch,
)

import mlflow.tracking
from pandas import DataFrame


class TestNeptuneExporter:
    def test_tracking_uri_set(self, neptune_exporter):
        assert mlflow.tracking.get_tracking_uri() == "test_tracking_uri"

    def test_get_existing_neptune_run_ids_for_empty_project(self, neptune_exporter):
        with patch("neptune.metadata_containers.metadata_containers_table.Table.to_pandas", return_value=DataFrame()):
            assert neptune_exporter._get_existing_neptune_run_ids() == set()

    def test_export_project_metadata(self, neptune_exporter):
        experiment = MagicMock()
        experiment.experiment_id = "test_id"
        experiment.tags = {"tag1": "value1", "tag2": "value2"}
        experiment.name = "test_name"
        experiment.creation_time = 1683197418954
        experiment.last_update_time = 1683197418954

        neptune_exporter._export_project_metadata(experiment)

        assert neptune_exporter.project["test_id/name"].fetch() == "test_name"
        assert neptune_exporter.project["test_id/tags"].fetch() == {"tag1": "value1", "tag2": "value2"}
        assert neptune_exporter.project["test_id/creation_time"].fetch() == datetime.fromtimestamp(
            experiment.creation_time / 1e3
        )
        assert neptune_exporter.project["test_id/last_update_time"].fetch() == datetime.fromtimestamp(
            experiment.last_update_time / 1e3
        )
