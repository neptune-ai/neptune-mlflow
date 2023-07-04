## neptune-mlflow 1.0.0

### Changes
- Updated MLflow exporter to work with the current neptune.ai API ([#40](https://github.com/neptune-ai/neptune-mlflow/pull/40))
- Misc Fixes: ([#44](https://github.com/neptune-ai/neptune-mlflow/pull/44))
    - Stop capturing hardware metrics
    - Map MLflow `run_name` to `sys/name` in Neptune `Run`

### Fixes
- Fix to support Python 3.7 and 3.8 ([#43](https://github.com/neptune-ai/neptune-mlflow/pull/43))
