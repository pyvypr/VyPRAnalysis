Querying Objects
=================================================

Querying objects stored by VyPR during monitoring is the main purpose of VyPR Analysis.  We currently provide
two main functions that are accessible directly via the top-level ``VyPRAnalysis`` package.

.. autofunction:: VyPRAnalysis.orm.operations.list_functions

.. autofunction:: VyPRAnalysis.orm.operations.list_test_data

A simple script that you could write with these is

.. code-block:: python

    import VyPRAnalysis as va
    va.set_server("http://localhost:8080/")
    functions = va.list_functions()
    test_executions = va.list_test_data()

``functions`` and ``test_executions`` are then lists that you can iterate through

.. code-block:: python

    for function in functions:
        print(function)

where each value of ``function`` is an instance of the ``Function`` class described in :doc:`orm-classes`.

The situation is similar for the code

.. code-block:: python

    for test_execution in test_executions:
        print(test_execution)