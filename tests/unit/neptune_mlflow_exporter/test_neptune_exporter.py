import mlflow.tracking


class TestNeptuneExporter:
    def test_tracking_uri_set(self, neptune_exporter):
        assert mlflow.tracking.get_tracking_uri() == "test_tracking_uri"
