# neptune-mlflow

> **Note**
>
> _This integration is still being updated for the main Neptune client library. It is currently only available for the Neptune legacy API._

---

![mlflow neptune.ai integration](docs/_static/mlflow_neptuneml.png)

## Overview

`neptune-mflow` integrates MLflow with Neptune to let you get the best of both worlds.
Enjoy tracking and reproducibility of MLflow with the organization and collaboration of Neptune.

With `neptune-mlflow` you can have your MLflow experiment runs hosted in a beautiful knowledge repo that lets you invite and manage project contributors.

All you need to do is go to your MLflow project and run:

```
neptune mlflow --project USER_NAME/PROJECT_NAME
```

and you have your experiments organized and easily shareable with the world.

## Documentation

See [neptune-mlflow docs](https://docs-legacy.neptune.ai/integrations/mlflow.html) for more info.

## Get started

### Register

Go to [neptune.ai](https://neptune.ai/?utm_source=github&utm_medium=repository&utm_campaign=integration-mlflow&utm_content=homepage) and sign up.

It is completely free for individuals and non-organizations, and you can invite others to join your team!

### Get your API token

In the bottom-left corner, click your user menu and select **Get your API token**.

### Set NEPTUNE_API_TOKEN environment variable

Go to your console and run:

```
export NEPTUNE_API_TOKEN='your_long_api_token'
```

### Create your first project

Click **All projects** &rarr; **New project**. Choose a name for it and whether you want it public or private.

## Install lib

```bash
pip install neptune-mlflow
```

## Sync your mlruns with Neptune

```bash
neptune mlflow --project USER_NAME/PROJECT_NAME
```

## Explore and Share

You can now explore and organize your experiments in Neptune, and share it with anyone:

* by sending a link to your project, experiment or chart if it is public
* or invite people to your project if you want to keep it private!

## Getting help

If you get stuck, don't worry. We are here to help.

The best order of communication is:

 * [GitHub issues](https://github.com/neptune-ai/neptune-mlflow/issues)
 * [Email](mailto:support@neptune.ai)

## Contributing

If you see something that you don't like, you are more than welcome to contribute!

There are many options:

* Submit a feature request or a bug here, on Github
* Submit a pull request that deals with an open feature request or bug
* Spread the word about Neptune in your community
