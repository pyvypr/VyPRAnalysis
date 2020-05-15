The Object-Relational Mapping
=================================================

The centre of VyPR's analysis library is its Object-Relational Mapping.  This is a set of classes that map to
objects stored by VyPR during program monitoring.

The ORM provides two levels: *factory functions* and *classes*.  Factory functions can generate one or more
instances of classes depending on whether the inputs given to them identify multiple objects in the database.

All factory functions and classes are accessible via the top-level ``VyPRAnalysis`` package.  For example, you can
write

.. code-block:: python

    import VyPRAnalysis as va
    va.set_server("http://localhost:8080/")
    prop = va.property(hash="...")

Factory Functions
-------------------------------------------------

.. automodule:: VyPRAnalysis.orm.base_classes
   :noindex:
   :members: function, function_call, property, binding, test_data, verdict, transaction, observation

Classes
-------------------------------------------------

.. automodule:: VyPRAnalysis.orm.base_classes
   :noindex:
   :members: Function, FunctionCall, Property, Binding, TestData, Verdict, Transaction, Observation