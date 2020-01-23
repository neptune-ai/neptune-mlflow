# neptune-mlflow
[![Build Status](https://travis-ci.org/neptune-ai/neptune-mlflow.svg?branch=master)](https://travis-ci.org/neptune-ai/neptune-mlflow)

![mlflow neptune.ai integration](docs/_static/mlflow_neptuneml.png)

# Overview
`neptune-mflow` integrates `mlflow` with `Neptune` to let you get the best of both worlds.
Enjoy tracking and reproducibility of `mlflow` with organization and collaboration of `Neptune`.

With `neptune-mlflow` you can have your `mlflow` experiment runs hosted in a beautiful knowledge repo that lets you invite and manage project contributors. 

All you need to do is go to your `mlflow` project and run:

```
neptune mlflow --project USER_NAME/PROJECT_NAME
```

and you have your [experiments](https://ui.neptune.ai/jakub-czakon/mlflow-integration/experiments) organized:

![image](https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/84068b5ff66719923006f798c21181cab6ec71df/mlflow_p1.png)

and easily [shareable](https://ui.neptune.ai/jakub-czakon/mlflow-integration/e/MLFLOW-10/output?path=artifacts%2F) with the world:

![image](https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/2b3989499b90a93e75208d9f9df5fa537b82b7fd/mlflow_artifact.png)

# Documentation
See [neptune-mlflow docs](https://docs.neptune.ai/integrations/mlflow.html) for more info.

# Get started

## Register
Go to [neptune.ai](https://neptune.ai/?utm_source=github&utm_medium=repository&utm_campaign=integration-mlflow&utm_content=homepage) and sign up.

It is completely free for individuals and non-organizations, and you can invite others to join your team!

## Get your API token
In order to start working with Neptune you need to get the API token first.
To do that, click on the `Get API Token` button on the top left.

![image](https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/e3776e605fea1fd5377c3ec748ba87b71cd8ef12/get_api_token.png)

## Set NEPTUNE_API_TOKEN environment variable
Go to your console and run:

```
export NEPTUNE_API_TOKEN='your_long_api_token'
```

## Create your first project
Click on `Projects` and the `New project`. Choose a name for it and whether you want it public or private.

![image](https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/e3776e605fea1fd5377c3ec748ba87b71cd8ef12/new_project.png)

## Install lib

```bash
pip install neptune-mlflow
```

## Sync your mlruns with Neptune

```bash
neptune mlflow --project USER_NAME/PROJECT_NAME
```

## Explore and Share
You can now explore and organize your experiments in Neptune:

![image](https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/84068b5ff66719923006f798c21181cab6ec71df/mlflow_p1.png)

And share it with anyone by sending a link to your project, experiment or chart if it is public
or invite people to your project if you want to keep it private!

![image](https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/e3776e605fea1fd5377c3ec748ba87b71cd8ef12/invite.png)

# Getting help
If you get stuck, don't worry we are here to help.
The best order of communication is:

 * [neptune community spectrum](https://spectrum.chat/neptune-community)
 * [neptune-mlflow docs](https://docs.neptune.ai/integrations/mlflow.html)
 * [github issues](https://github.com/neptune-ai/neptune-mlflow/issues) 

# Contributing
If you see something that you don't like you are more than welcome to contribute!
There are many options:

  * Participate in discussions on [neptune community spectrum](https://spectrum.chat/neptune-community)
  * Submit a feature request or a bug here, on Github
  * Submit a pull request that deals with an open feature-request or bug
  * Spread a word about neptune-contrib in your community
