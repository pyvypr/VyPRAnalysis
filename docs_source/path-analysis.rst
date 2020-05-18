Path Analysis
=================================================

VyPR records information about the paths taken by monitored functions at runtime.  You can use the analysis library
to analyse the monitored program's performance with respect to these paths and various operations you can perform
with them.

Preamble
-------------------------------------------------

Path analysis requires access to the source code of the monitored service.  You can tell the analysis library
where to find your service using the ``set_monitored_service_path`` configuration function.  You can read more about
this at :doc:`config-functions`.

Once the analysis library knows where to find your service's code, path analysis with VyPR's analysis library
starts one of two ways:

1. You use ``Observation`` instances to determine paths taken by function calls to reach them.  In this case,
calling ``reconstruct_reaching_path`` on each ``Observation`` instance will give the path taken to reach that
observation.

2. You use a ``FunctionCall`` instance to determine the path taken through a function by a specific call.  In this case,
calling ``reconstruct_path`` on the ``FunctionCall`` instance will give the path taken by that function call.  This
case is especially useful when combined with :doc:`call-trees`.

If you care about ``Observation`` instances, the natural next step is to look at the ``ObservationCollection`` class.

Observation Collections
-------------------------------------------------

The basis of the analysis library's path comparison facilities is the ``ObservationCollection`` class.

The idea is that, once you have a list of ``Observation`` objects (:doc:`reference/orm-base-classes`),
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
   :members: intersection, __sub__

Calling ``intersection`` on ``PathCollection`` instances gives a ``ParametricPathCollection`` instance and
calling ``intersection`` on ``PartialPathCollection`` instances gives a ``PartialParametricPathCollection`` instance.

.. autoclass:: VyPRAnalysis.orm.operations.PartialParametricPathCollection
   :noindex:
   :members:

.. autoclass:: VyPRAnalysis.orm.operations.ParametricPathCollection
   :noindex:
   :members:

Variants of Path Collections
-------------------------------------------------

.. autoclass:: VyPRAnalysis.orm.operations.PartialPathCollection
   :noindex:
   :members: