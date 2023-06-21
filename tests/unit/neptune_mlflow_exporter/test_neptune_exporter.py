class TestNeptuneExporter:
    def test_client_received_correct_tracking_uri(self, neptune_exporter):
        assert neptune_exporter.mlflow_client.tracking_uri == "test_tracking_uri"
