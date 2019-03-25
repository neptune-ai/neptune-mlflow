neptune-mlflow: MLflow integration with Neptune
===========================================
 
This library integrates `MLflow`_ with `Neptune`_ to let you get the best of both worlds.
Enjoy tracking and reproducibility of `MLflow`_ with organizion and collaboration of `Neptune`_.

With `neptune-mlflow` you can have your `MLflow`_ experiment runs hosted in a beatutiful knowledge repo that lets you invite and manage project contributors. 
 
With one simple command:

    neptune mlflow --project USER_NAME/PROJECT_NAME
    
Organize your mlflow experiments: 

.. figure:: https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/84068b5ff66719923006f798c21181cab6ec71df/mlflow_p1.png
   :alt: image
   
   
and share you work with others.

.. figure:: https://gist.githubusercontent.com/jakubczakon/f754769a39ea6b8fa9728ede49b9165c/raw/2b3989499b90a93e75208d9f9df5fa537b82b7fd/mlflow_artifact.png
   :alt: image
   

.. toctree::
   :maxdepth: 1
   :caption: Get Started

   neptune_app
   library
   
   
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
.. _MLflow: https://mlflow.org/
.. _Neptune: http://bit.ly/2YnX5Vs
.. _Neptune community forum: https://community.neptune.ml/
.. _Github projects: https://github.com/neptune-ml/neptune-mlflow/projects
.. _Neptune Slack: https://neptune-community.slack.com
.. _Neptune Slack Join: https://join.slack.com/t/neptune-community/shared_invite/enQtNTI4Mjg3ODk2MjQwLWE5YjI0YThiODViNDY4MDBlNmRmZTkwNTE3YzNiMjQ5MGM2ZTFhNzhjN2YzMTIwNDM3NjQyZThmMDk1Y2Q1ZjY
