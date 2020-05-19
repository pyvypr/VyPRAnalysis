Call Trees
=================================================

If you write your queries over multiple functions that call each other, VyPR's analysis library can be used
to construct a call tree based on the top-level transaction.  For example, if you're monitoring a web service,
then there will be a transaction for each HTTP request and, from there, you will be able to reconstruct the
call tree(s) associated with that HTTP request.

.. autoclass:: VyPRAnalysis.interprocedural.CallTree
   :members: get_direct_callees, get_reachable, get_vertex_from_call, write_to_file

Here's an example of how you could use Call Trees.  First, import everything you need and establish a connection

.. code-block:: python

    import VyPRAnalysis as va
    import VyPRAnalysis.interprocedural.CallTree as CallTree
    va.set_server("http://localhost:8080/")

Then, choose a function and gets a list of its calls

.. code-block:: python

    particular_function = va.list_functions()[0]
    calls = particular_function.get_calls()

Finally, loop through the calls and, for each one, instantiate the call tree of that call's transaction

.. code-block:: python

    for call in calls:
        transaction = va.transaction(call.trans)
        call_tree = CallTree(transaction)

Call trees then work based on individual function calls.  For example, if you have a variable ``call`` that contains
a call to a function that you know is in a call tree, you can explore the call tree with

.. code-block:: python

    callees = call_tree.get_direct_callees(call)

And if you don't already know about any calls but want to find all callees (either indirect or direct), you can use

.. code-block:: python

    callees = call_tree.get_reachable()