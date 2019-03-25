neptune-mlflow: MLflow integration with Neptune
===========================================

This library is a collection of helpers and extensions that make working
with `Neptune website`_ more effective and better. It is build on top of neptune-cli
and neptune-lib and gives you option to do things like:
 * interactive visualizations of experiment runs or hyperparameters
 * running hyper parameter sweeps in scikit-optimize, hyperopt or any other tool you like
 * monitor training of the lightGBM models
 * much more
 
.. figure:: https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/d7c844854a9c31c7fea317e41ee77ec16c3bb7eb/contrib_hyper22.png
   :alt: image
   
   
Get Started
-----------------------

Register to Neptune.

Create a project.

Set NEPTUNE_API_TOKEN.


Install neptune-contrib via pip:

    $ pip install neptune-mlflow 
    
    
Sync your mlflow project:

    $ neptune mlflow --project USER_NAME/PROJECT_NAME


.. toctree::
   :maxdepth: 1
   :caption: Examples

   examples/examples_index

.. toctree::
   :maxdepth: 1
   :caption: User Guide

   data_loader <user_guide/data_loader>
   sync <user_guide/sync>
   

Bug Reports and Questions
-----------------------

neptune-mlflow is an Apache Licence 2.0 project and the source code is available on `GitHub`_. If you
find yourself in any trouble drop an isse on `Git Issues`_, fire a feature request on
`Git Feature Request`_ or ask us on the `Neptune community forum`_ or `Neptune Slack`_.

You can join our slack by clicking on the `Neptune Slack Join`_.


Contribute
-----------------------

We keep an updated list of open issues/feature ideas on github project page `Github projects`_.
If you feel like taking a shot at one of those do go for it!
In case of any trouble please talk to us on the `Neptune Slack`_.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`


.. _GitHub: https://github.com/neptune-ml/neptune-mlflow
.. _Git Issues: https://github.com/neptune-ml/neptune-mlflow/issues
.. _Git Feature Request: https://github.com/neptune-ml/neptune-mlflow/issues
.. _Neptune website: https://neptune.ml/
.. _Neptune community forum: https://community.neptune.ml/
.. _Github projects: https://github.com/neptune-ml/neptune-mlflow/projects
.. _Neptune Slack: https://neptune-community.slack.com
.. _Neptune Slack Join: https://join.slack.com/t/neptune-community/shared_invite/enQtNTI4Mjg3ODk2MjQwLWE5YjI0YThiODViNDY4MDBlNmRmZTkwNTE3YzNiMjQ5MGM2ZTFhNzhjN2YzMTIwNDM3NjQyZThmMDk1Y2Q1ZjY
