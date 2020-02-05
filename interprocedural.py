"""
Module for inter-procedural analysis.
Prototype stage.
"""
from .orm import transaction
import pprint


def scfg_element_to_dot(scfg_obj):
    """Gives a string that can be used by dot for drawing parse trees."""
    return str(scfg_obj).replace("<", "").replace(">", "")


class CallTreeVertex(object):
    """Models a vertex in a class tree."""

    def __init__(self, tree, call_obj=None):
        self._call_obj = call_obj
        self._children = []
        tree._vertices.append(self)

    def __repr__(self):
        return "<CallTreeVertex (%s)>" % (self._call_obj)

    def add_child(self, vertex):
        self._children.append(vertex)

    def get_callees(self):
        return self._children


class CallTree(object):
    """Models a graph structure derived from the list of calls that happened during a transaction/http request.
    Note: we have a tree because, even with recursion, vertices are calls, and not
    actual functions, so we cannot have cycles."""

    def __init__(self, transaction):
        """
        Given transaction, get all calls that happened during it and construct a tree.
        Take into account the fact that multiple machines may have generated calls, in which case, if we process
        a call with no child calls, we search for a transaction occurring during that call from another machine.
        """

        self._vertices = []

        self._all_calls = transaction.get_calls()
        self._all_calls.sort(key=lambda call: call.time_of_call)

        pprint.pprint(self._all_calls)

        # construct root containing the transaction
        self._root = CallTreeVertex(self, transaction)

        # construct the tree, starting at the transaction root
        self.process_vertex(self._root, self._all_calls)

    def __repr__(self):
        return "<CallTree>"

    def add_vertex(self, vertex):
        self._vertices.append(vertex)

    def get_direct_callees(self, call):
        """Given a call, find its vertex and then return its children."""
        relevant_vertex = \
        list(filter(lambda vertex: vertex._call_obj != None and vertex._call_obj.id == call.id, self._vertices))[0]
        direct_callees = list(map(lambda vertex : vertex._call_obj, relevant_vertex.get_callees()))
        return direct_callees

    def process_vertex(self, root, calls):
        """Given a root and a list of child calls, construct the subtree rooted here."""

        # copy the list so we don't modify
        # the list used after the recursive call
        calls = [c for c in calls]

        while len(calls) > 0:
            # find the earliest call in the list
            # this is the first, since they're already sorted
            earliest_call = calls[0]

            # construct a root vertex
            new_vertex = CallTreeVertex(self, earliest_call)

            # add a child vertex to the root
            root.add_child(new_vertex)

            # remove what we just used
            calls.remove(earliest_call)

            # find the end time of the root, and then find all calls in the list
            # whose start times are before that
            end_time = earliest_call.end_time_of_call
            start_time = earliest_call.time_of_call
            # note: start time is necessarily before end time so we only need to check the bounds
            callees = list(filter(
                lambda call: call.time_of_call > start_time and call.end_time_of_call < end_time, calls
            ))

            if len(callees) > 0:

                # process the callees by constructing a new subtree

                # expand the subtree
                self.process_vertex(new_vertex, callees)

                # remove the calls we've just processed
                calls = list(set(calls) - set(callees))

            else:
                # there are no callees, so look for a transaction
                print("looking for a transaction within the times %s and %s" %
                      (earliest_call.time_of_call, earliest_call.end_time_of_call))
                relevant_transactions = transaction(
                    time_lower_bound=earliest_call.time_of_call, time_upper_bound=earliest_call.end_time_of_call
                )

                if len(relevant_transactions) != 0:
                    # construct the call tree of the transaction and attach it to new_vertex as a subtree
                    subtree = CallTree(relevant_transactions[0])
                    self.add_subtree_to_vertex(new_vertex, subtree)
                else:
                    print("None found - no other machine generated data during the call %s" % earliest_call)

    def add_subtree_to_vertex(self, vertex, subtree):
        """
        Given a CallTreeVertex and a CallTree, add the root of the call tree as a child of the vertex
        and copy all vertices over into the vertex set of the call tree.
        :param vertex:
        :param subtree:
        :return: None
        """
        vertex.add_child(subtree._root)
        self._vertices += subtree._vertices

    def write_to_file(self, file_name):
        """Write this call tree to a dot file."""
        from graphviz import Digraph

        graph = Digraph()
        graph.attr("graph", splines="true", fontsize="10")
        shape = "rectangle"
        for vertex in self._vertices:
            colour = "black"
            graph.node(str(id(vertex)), scfg_element_to_dot(vertex._call_obj), shape=shape, color=colour)
            for child in vertex._children:
                graph.edge(
                    str(id(vertex)),
                    str(id(child))
                )
        graph.render(file_name)
        print("Written call tree to file '%s'." % file_name)
