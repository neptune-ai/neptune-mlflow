from neptune_mlflow_plugin import MlflowPlugin

try:
    from neptune import (
        Project,
        init_project,
        init_run,
    )
except ImportError:
    from neptune.new import init_project, init_run
    from neptune.new.metadata_containers import Project

import pytest
import tensorflow as tf

from neptune_mlflow_exporter.impl import NeptuneExporter


@pytest.fixture(scope="session")
def dataset():
    x_train = tf.random.uniform(shape=[2, 28, 28])
    y_train = tf.constant([1, 1], shape=(2, 1), dtype=tf.int8)
    x_test = tf.random.uniform(shape=[2, 28, 28])
    y_test = tf.constant([1, 1], shape=(2, 1), dtype=tf.int8)

    return (x_train, y_train), (x_test, y_test)


@pytest.fixture(scope="session")
def model():
    model = tf.keras.models.Sequential(
        [
            # We are *not* providing input_size to the first layer, so the test will catch also the case where the
            # model was not build yet: https://stackoverflow.com/q/55908188/3986320
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(10),
        ]
    )
    lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate=1e-2, decay_steps=10000, decay_rate=0.9
    )
    optimizer = tf.keras.optimizers.SGD(learning_rate=lr_schedule)

    loss_fn = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    model.compile(optimizer=optimizer, loss=loss_fn, metrics=["accuracy"])
    return model


@pytest.fixture(scope="session")
def neptune_project() -> Project:
    with init_project(mode="debug", project="organization/project") as project:
        yield project


@pytest.fixture(scope="session")
def neptune_exporter(neptune_project) -> NeptuneExporter:
    yield NeptuneExporter(project=neptune_project, mlflow_tracking_uri="test_tracking_uri")


@pytest.fixture(scope="session")
def neptune_exporter_e2e() -> NeptuneExporter:
    project = init_project()
    yield NeptuneExporter(project, exclude_artifacts=False)


@pytest.fixture(scope="session")
def mlflow() -> MlflowPlugin:
    with init_run(mode="debug") as run:
        yield MlflowPlugin(
            neptune_run=run,
        )
