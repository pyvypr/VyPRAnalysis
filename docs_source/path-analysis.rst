Path Analysis
=================================================

VyPR records information about the paths taken by monitored functions at runtime.  You can use the analysis library
to analyse the monitored program's performance with respect to these paths and various operations you can perform
with them.

Observation Collections
-------------------------------------------------

The basis of the analysis library's path comparison facilities is the ``ObservationCollection`` class.

The idea is that, once you have a list of ``Observation`` objects (:doc:`references/orm-base-classes`),
you can form an ``ObservationCollection`` object, which provides methods that reconstruct the paths taken by
the relevant monitored functions to reach the observations given.

.. autoclass:: VyPRAnalysis.orm.operations.ObservationCollection
   :noindex:
   :members:

Path Collections
-------------------------------------------------

A ``PathCollection`` instance is obtained by calling the ``to_paths`` method defined on ``ObservationCollection``
instances.

The key method defined on instances of ``PathCollection`` is ``intersection``.

.. autoclass:: VyPRAnalysis.orm.operations.PathCollection
   :noindex:
   :members: intersection

Variants of Path Collections
-------------------------------------------------

.. autoclass:: VyPRAnalysis.orm.operations.ParametricPathCollection
   :noindex:
   :members:

.. autoclass:: VyPRAnalysis.orm.operations.PartialPathCollection
   :noindex:
   :members:

.. autoclass:: VyPRAnalysis.orm.operations.PartialParametricPathCollection
   :noindex:
   :members: