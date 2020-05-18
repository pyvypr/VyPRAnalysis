Configuring VyPR Analysis
=================================================

The VyPR Analysis provides a set of configuration functions that allow you to configure your analysis as you need.

All of these functions are accessible via the top-level ``VyPRAnalysis`` package.

The first set of functions should each be used in a distinct scenario.  ``set_server`` assumes that a verdict server
is already running and attempts to connect to it, whereas ``prepare`` is useful if you have a database file and
want to perform some local analysis.

.. automodule:: VyPRAnalysis
   :members: set_server, prepare

Some facilities provided by the analysis library require access to the source code of the monitored service.
You can tell them where to find it using the ``set_monitoring_service_path`` function.

.. autofunction:: VyPRAnalysis.set_monitored_service_path