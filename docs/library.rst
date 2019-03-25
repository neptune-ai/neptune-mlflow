.. _library:
    
Library
============

**Install lib**

It can be easily installed from the console.

     pip install neptune-mlflow

**Sync your mlruns with Neptune**

Now you should navigate to your MLflow project and run:

     neptune mlflow --project USER_NAME/PROJECT_NAME
    
You can also point to your MLflow project directory:

     neptune mlflow /PATH/TO/MLflow_PROJECT --project USER_NAME/PROJECT_NAME