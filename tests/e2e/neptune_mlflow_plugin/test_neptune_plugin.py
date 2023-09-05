import os.path

import mlflow
import numpy as np
from neptune import Run

from neptune_mlflow_plugin import create_neptune_tracking_uri


def test_e2e():
    uri = create_neptune_tracking_uri(
        name="test_name",
        description="test description",
        monitoring_namespace="test_monitoring",
        tags={"test", "mlflow"},
    )
    mlflow.set_tracking_uri(uri)

    assert mlflow.get_tracking_uri() == uri

    with mlflow.start_run() as run:
        mlflow_run_id_1 = run.info.run_id

        mlflow.set_tag("mytag", "myvalue")
        for i in range(10):
            mlflow.log_metric("some_key", i, step=i)

        mlflow.log_artifact("README.md")

        mlflow.log_param("lr", 0.0001)
        mlflow.log_dict({"a": "b"}, "file.json")

        image = np.random.randint(0, 256, size=(100, 100, 3), dtype=np.uint8)
        mlflow.log_image(image, "image.png")

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot([0, 1], [2, 3])

        mlflow.log_figure(fig, "figure.png")

    with mlflow.start_run() as run:
        mlflow_run_id_2 = run.info.run_id
        mlflow.log_artifacts("docs", "my_docs")

        mlflow.artifacts.download_artifacts(run_id=mlflow_run_id_2, artifact_path="my_docs", dst_path="downloaded_docs")

        mlflow.log_artifact("CHANGELOG.md", "changelog")

        mlflow.artifacts.download_artifacts(
            run_id=mlflow_run_id_2, artifact_path="changelog", dst_path="downloaded_changelog"
        )

    assert mlflow_run_id_1 != mlflow_run_id_2  # make sure those are two different Neptune runs

    with Run(custom_run_id=mlflow_run_id_1) as neptune_run:
        assert neptune_run["sys/tags"].fetch() == {"test", "mlflow", "myvalue", "mytag"}
        assert float(neptune_run["lr"].fetch()) == 0.0001
        assert neptune_run.exists("figure")
        assert neptune_run.exists("file")
        assert neptune_run.exists("image")
        assert neptune_run["some_key"].fetch_values().shape == (10, 3)
        assert neptune_run.exists("README")

    with Run(custom_run_id=mlflow_run_id_2):
        assert os.path.isdir("downloaded_docs")
        assert os.path.isdir("downloaded_changelog")
