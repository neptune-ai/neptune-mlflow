# Neptune + MLflow integration

Neptune is a lightweight experiment tracker that offers a single place to track, compare, store, and collaborate on experiments and models. 

This integration lets you enjoy tracking and reproducibility of MLflow with the organization and collaboration of Neptune. You can have your MLflow experiment runs hosted in a knowledge repo where you can invite and manage project contributors, while not having to change your MLflow logging code.

Should you wish to switch to Neptune, you can migrate your MLflow data to Neptune with the exporter tool.

## What will you get with this integration?

- A **plugin** which you can use to send your MLflow-logged metadata to Neptune with the help of a tracking URI.
- An **exporter** for migrating existing MLflow experiments to your Neptune project.

## Resources

* [Documentation](https://docs.neptune.ai/integrations/mlflow)
* [Code examples on GitHub](https://github.com/neptune-ai/examples/blob/main/integrations-and-supported-tools/mlflow/scripts)
* [Run logged in the Neptune app](https://app.neptune.ai/o/common/org/mlflow-integration/runs/details?viewId=standard-view&detailsTab=metadata&shortId=MLFLOW-515&type=run)
* [Run example in Google Colab](https://colab.research.google.com/github/neptune-ai/examples/blob/main/integrations-and-supported-tools/mlflow/notebooks/Neptune_Mlflow.ipynb)

## Example

On the command line:

```
pip install neptune-mlflow
```

Send your MLflow-logged metadata to Neptune (in Python):

```python
import mlflow
from neptune_mlflow_plugin import create_neptune_tracking_uri

# Create a Neptune tracking URI
neptune_uri = create_neptune_tracking_uri(
    api_token=ANONYMOUS_API_TOKEN,  # Set as environment variable or replace with your own token
    project="common/mlflow-integration",  # Set as environment variable or replace with your own project
    tags=["mlflow", "plugin"],  # (optional) use your own
)

mlflow.set_tracking_uri(neptune_uri)

with mlflow.start_run():
    ...
```

Export existing MLflow runs to Neptune:

```
neptune mlflow --project your-neptune-workspace/your-neptune-project
```

## Support

If you got stuck or simply want to talk to us, here are your options:

* Check our [FAQ page](https://docs.neptune.ai/getting_help)
* You can submit bug reports, feature requests, or contributions directly to the repository
* Chat! When in the Neptune application click on the blue message icon in the bottom-right corner and send a message. A real person will talk to you ASAP (typically very ASAP)
* You can just shoot us an email at support@neptune.ai
