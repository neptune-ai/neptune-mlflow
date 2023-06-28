import mlflow
import mlflow.keras
import mlflow.tensorflow
import neptune

EPOCHS = 1
BATCH_SIZE = 1
MODEL_NAME = "test_model"
MLFLOW_EXPERIMENT_NAME = "E2E neptune experiment"
MLFLOW_RUN_TAGS = {
    "tag1": "value1",
    "tag2": "value2",
}


def train(dataset, model):
    mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
    mlflow.keras.autolog()

    with mlflow.start_run() as run:
        mlflow.set_tags(MLFLOW_RUN_TAGS)
        run_id = run.info.run_id

        (x_train, y_train), (x_test, y_test) = dataset

        model.fit(
            x_train,
            y_train,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            validation_data=(x_test, y_test),
        )
        test_loss, test_acc = model.evaluate(x_test, y_test)

        mlflow.log_param("epochs", EPOCHS)
        mlflow.log_param("batch_size", BATCH_SIZE)

        mlflow.log_metric("test_acc", test_acc)
        mlflow.log_metric("test_loss", test_loss)

        # Save as TensorFlow SavedModel format (MLflow Keras default)
        mlflow.keras.log_model(model, "keras-model", registered_model_name=MODEL_NAME)

        # write model summary
        summary = []
        model.summary(print_fn=summary.append)
        summary = "\n".join(summary)
        with open("model_summary.txt", "w") as f:
            f.write(summary)
        mlflow.log_artifact("model_summary.txt")
    return run_id


def test_e2e(dataset, model, neptune_exporter_e2e):

    run_id = train(dataset, model)

    neptune_exporter_e2e.run()

    # check logged project metadata
    experiment = mlflow.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    mlflow_runs = mlflow.search_runs(experiment_names=[MLFLOW_EXPERIMENT_NAME])
    run_name = mlflow_runs["tags.mlflow.runName"][0]

    # check logged run metadata
    neptune_run = neptune.init_run(custom_run_id=run_id)

    # experiment
    assert neptune_run["experiment/experiment_id"].fetch() == experiment.experiment_id
    assert neptune_run["experiment/name"].fetch() == MLFLOW_EXPERIMENT_NAME
    assert neptune_run.exists("experiment/creation_time")
    assert neptune_run.exists("experiment/last_update_time")

    # run info
    assert neptune_run["run_info/lifecycle_stage"].fetch() == "active"
    assert neptune_run.exists("run_info/status")
    assert neptune_run["run_info/run_name"].fetch() == run_name
    # Currently, client overwrites `sys/name` when run is re-opened
    # with `custom_run_id`.
    # assert neptune_run["sys/name"].fetch() == run_name

    # run data
    assert set(MLFLOW_RUN_TAGS.items()).issubset(set(neptune_run["run_data/tags"].fetch().items()))

    assert neptune_run.exists("run_data/metrics/accuracy")
    assert neptune_run.exists("run_data/metrics/test_loss")
    assert neptune_run.exists("run_data/metrics/val_accuracy")
    assert neptune_run.exists("run_data/metrics/loss")

    assert int(neptune_run["run_data/params/epochs"].fetch()) == EPOCHS
    assert int(neptune_run["run_data/params/batch_size"].fetch()) == BATCH_SIZE

    # logged artifacts
    assert neptune_run.exists("artifacts/model_summary.txt")
    assert neptune_run.exists("artifacts/keras-model")
    assert neptune_run.exists("artifacts/tensorboard_logs")
