from unittest.mock import patch

import mlflow.tracking
from pandas import DataFrame


class TestNeptuneExporter:
    def test_tracking_uri_set(self, neptune_exporter):
        assert mlflow.tracking.get_tracking_uri() == "test_tracking_uri"

    def test_get_existing_neptune_run_ids_for_empty_project(self, neptune_exporter):
        with patch("neptune.metadata_containers.metadata_containers_table.Table.to_pandas", return_value=DataFrame()):
            assert neptune_exporter._get_existing_neptune_run_ids() == set()
