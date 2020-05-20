"""
**Operations to begin analyses with**
"""

import requests
import json
import os

# VyPR imports
import VyPR.SCFG.construction
from VyPR.SCFG.parse_tree import ParseTree

# VyPRAnalysis imports
from VyPRAnalysis import get_server, get_connection, get_monitored_service_path
from VyPRAnalysis.orm.base_classes import (function,
                                           function_call,
                                           verdict,
                                           observation,
                                           instrumentation_point,
                                           test_data)
from VyPRAnalysis.path_reconstruction import edges_from_condition_sequence, deserialise_condition


"""
Entry-point functions for listing objects held in the database.
"""


def list_functions():
    """
    Get a list of all existing functions from the server.
    """
    connection = get_connection()
    result = connection.request('client/function/')
    if result == "None":
        raise ValueError('No functions currently exist.')
    f_dict = json.loads(result)
    f_list = []
    for f in f_dict:
        f_obj = function(f["id"], f["fully_qualified_name"])
        f_list.append(f_obj)
    return f_list


def list_test_data():
    """
    Get a list of all existing test cases from the server.
    """
    connection = get_connection()
    result = connection.request('client/test_data/')
    if result == "None":
        raise ValueError('No test cases currently exist.')
    results = json.loads(result)
    test_case_objs = []
    for test_case_row in results:
        test_case_obj = test_data(
            test_case_row["id"],
            test_case_row["test_name"],
            test_case_row["test_result"],
            test_case_row["start_time"],
            test_case_row["end_time"]
        )
        test_case_objs.append(test_case_obj)
    return test_case_objs

"""
Post-processing functions.
"""


def get_parametric_path(obs_id_list, instrumentation_point_id=None):
    # instrumentation_point optional -> get it from an observation in the list
    if instrumentation_point_id == None:
        instrumentation_point_id = observation(obs_id_list[0]).instrumentation_point

    # checking if all the observations are made at the same point
    for id in obs_id_list:
        obs = observation(id)
        if obs.instrumentation_point != instrumentation_point_id:
            raise ValueError('the observations must have the same instrumentation point')

    data1 = {"observation_ids": obs_id_list, "instrumentation_point_id": instrumentation_point_id}
    req = requests.post(url=get_server() + 'client/get_parametric_path/', data=json.dumps(data1))

    return req.text


def get_intersection_from_observations(function_name, obs_id_list, inst_point=None):
    if inst_point == None:
        inst_point = observation(obs_id_list[0]).instrumentation_point

    # checking if all the observations are made at the same point
    for id in obs_id_list:
        obs = observation(id)
        if obs.instrumentation_point != inst_point:
            raise ValueError('the observations must have the same instrumentation point')

    f = function(fully_qualified_name=function_name)
    subchain_text = get_parametric_path(obs_id_list, inst_point)
    #    print(subchain_text)
    subchain_dict = json.loads(subchain_text)
    #    pprint(subchain_dict)

    seq = subchain_dict["intersection_condition_sequence"]
    scfg = f.get_graph()
    ipoint = instrumentation_point(inst_point)

    intersection_path = edges_from_condition_sequence(
        scfg,
        map(deserialise_condition, seq[1:]),
        ipoint.reaching_path_length
    )
    return intersection_path


def get_paths_from_observations(function_name, obs_id_list, inst_point=None):
    """
    returns a list of paths taken before each of the given observations
    """

    if inst_point == None:
        inst_point = observation(obs_id_list[0]).instrumentation_point

    # checking if all the observations are made at the same point
    for id in obs_id_list:
        obs = observation(id)
        if obs.instrumentation_point != inst_point:
            raise ValueError('the observations must have the same instrumentation point')

    f = function(fully_qualified_name=function_name)
    subchain_text = get_parametric_path(obs_id_list, inst_point)
    subchain_dict = json.loads(subchain_text)

    paths = []
    seq = subchain_dict["intersection_condition_sequence"]

    for id in obs_id_list:

        subchain = []
        ind = 0

        while ind < len(seq):
            if seq[ind] == "parameter":
                cond = ((subchain_dict["parameter_maps"])["0"])[str(obs_id_list.index(id))]
                for cond_elem in cond:
                    #                    print(cond_elem)
                    subchain.append(deserialise_condition(cond_elem))
            else:
                subchain.append(seq[ind])
            ind += 1

        subchain = subchain[1:]
        scfg = f.get_graph()
        ipoint = instrumentation_point(inst_point)
        path = edges_from_condition_sequence(scfg, subchain, ipoint.reaching_path_length)
        paths.append(path)

    return paths


"""
Path analysis classes.
"""


class Path(object):
    """
    Models a program path, which internally is a list of edges in a Symbolic Control-Flow Graph.
    """

    def __init__(self, edge_list):
        self._edge_list = edge_list


class ParametricPath(object):
    """
    Models a program path with a hole that can be filled by taking one of multiple possible paths.
    """

    def __init__(self, parametric_parse_tree):
        self._parse_tree = parametric_parse_tree
        self._edge_vertex_list = parametric_parse_tree.read_leaves()

    def get_parameter_value(self, parameter):
        """
        Get the subpath taken by the current path at ``parameter``.
        """
        return self._parse_tree.get_parameter_subtree(parameter.path).read_leaves()


class PathParameter(object):
    """
    Internal wrapper class for path parameters, so users don't have to deal with the lists of parse tree edges
    that are actually used in the implementation of path parameters.
    """

    def __init__(self, path, function_name):
        self.path = path
        self.function_name = function_name

    def __repr__(self):
        return "<PathParameter for line %i, function='%s'>" % (self.path[-1]._structure_obj.lineno, self.function_name)


class PathCollection(object):
    """
    Models a set of paths, obtained by direct reconstruction or modification of already reconstructed paths.
    """

    def __init__(self, paths, scfg, function_name, parametric=False):
        self._paths = paths
        self._scfg = scfg
        self._function_name = function_name
        self._parametric = parametric

    def __repr__(self):
        return "<%s paths=%s>" % \
               (
                   self.__class__.__name__,
                   "\n\n".join(map(str, self._paths))
               )

    def intersection(self, starting_vertex=None):
        """
        Return a ``ParametricPathCollection`` instance containing the single path resulting from the intersection
        of all paths in the current collection.
        """
        grammar = self._scfg.derive_grammar()

        parse_trees = map(
            lambda path: ParseTree(
                path,
                grammar,
                self._scfg.starting_vertices if not (starting_vertex) else starting_vertex,
                parametric=self._parametric
            ),
            self._paths
        )
        # determine intersection of the parse trees
        intersection_tree = parse_trees[0].intersect(parse_trees[1:])
        # determine path with parameters
        parametric_path = intersection_tree.read_leaves()
        # for any parameters in the path, determine the paths to those parameters
        path_parameters = []
        intersection_tree.get_parameter_paths(intersection_tree._root_vertex, [], path_parameters)
        path_parameters = map(lambda param : PathParameter(param, self._function_name), path_parameters)
        # construct the final path collection
        if not (starting_vertex):
            return ParametricPathCollection(
                [parametric_path],
                self._paths,
                path_parameters,
                self._scfg,
                self._function_name
            )
        else:
            return PartialParametricPathCollection(
                [parametric_path],
                self._paths,
                path_parameters,
                self._scfg,
                self._function_name
            )

    def show_critical_points_in_file(self, filename=None, verbose=False):
        """
        Write out a version of a monitored file with markers to show instructions where paths diverged that lead to
        observations that VyPR recorded diverged.
        """
        path = self.intersection()._paths[0]
        condition_lines = set()
        # doing this as a set to avoid highlighting the same lines multiple times
        for path_elem in path:
            if type(path_elem) is VyPR.control_flow_graph.construction.CFGVertex:
                condition_lines.add(path_elem._structure_obj.lineno)

        function_name = self._function_name
        last_dot = function_name.rfind('.')
        if last_dot == -1: function_name = ''
        function_name = function_name[0:last_dot]
        code_file_name = os.path.join(get_monitored_service_path(), function_name.replace('.', '/') + '.py.inst')
        file = open(code_file_name, "r")
        lines = file.readlines()
        for line_ind in condition_lines:
            lines[line_ind - 1] = '*' + lines[line_ind - 1]

        if verbose:
            for line in lines:
                print(line.rstrip())
        target_file = code_file_name + '_changed' if not (filename) else filename
        file = open(target_file, "w")
        file.writelines(lines)
        file.close()

    def critical_points_in_code(self):
        """
        Based on the intersection of the paths held by the current collection,
        determine the points of divergence in the relevant source code.
        """
        path = self.intersection()._paths[0]
        condition_lines = set()
        # doing this as a set to avoid highlighting the same lines multiple times
        for path_elem in path:
            if type(path_elem) is VyPR.control_flow_graph.construction.CFGVertex:
                condition_lines.add(path_elem._structure_obj.lineno)

        # determine range of the source code to show
        min_line = min(condition_lines) - 10
        max_line = max(condition_lines) + 10

        function_name = self._function_name
        last_dot = function_name.rfind('.')
        if last_dot == -1: function_name = ''
        function_name = function_name[0:last_dot]
        code_file_name = os.path.join(get_monitored_service_path(), function_name.replace('.', '/') + '.py.inst')
        file = open(code_file_name, "r")
        lines = file.readlines()

        for line_ind in condition_lines:
            lines[line_ind - 1] = '*' + lines[line_ind - 1]

        # add line numbers
        for n in range(len(lines)):
            lines[n] = "%i  %s" % ((n + 1), lines[n])

        # trim line list
        lines = lines[min_line:max_line]

        return "".join(lines)

    def merge(self, other_path_collection):
        """
        Add ``other_path_collection`` to the current list of paths.
        """
        self._paths += other_path_collection._paths

    def __sub__(self, other):
        """
        Gives a ``PartialPathCollection`` with path differences.
        """

        if len(self._paths) != len(other._paths):
            raise Exception("Cannot form a difference of sets of paths when sets have different sizes.")

        differences = []
        for (n, path) in enumerate(self._paths):
            # make sure we can subtract the paths
            if len(path) < len(other._paths[n]):
                raise Exception("To compute path_1 - path_2, path_2 cannot be longer than path_1.")
            # make sure the shorter path is actually a subpath
            for i in range(len(other._paths[n])):
                if path[i] != other._paths[n][i]:
                    raise Exception("path_1 - path_2 requires that path_2 is a subpath of path_1.")
            differences.append(path[len(other._paths[n]):])

        return PartialPathCollection(differences, self._scfg, self._function_name)


class ParametricPathCollection(PathCollection):
    """
    Models a collection of paths, all of which diverge at the same point in the source code and start at the beginning
    of the monitored function.
    """

    def __init__(self, paths, original_paths, path_parameters, scfg, function_name):
        PathCollection.__init__(self, paths, scfg, function_name, parametric=True)
        self._original_paths = original_paths
        self._path_parameters = path_parameters


class PartialPathCollection(PathCollection):
    """
    Models a collection of paths which do not start from the starting vertex of the Symbolic Control-Flow Graph.
    """

    def intersection(self):
        """
        Perform intersection, but such that the parse trees used
        are generated starting from the beginning of each path (we assume the paths
        start in the same place).
        """
        return super(PartialPathCollection, self).intersection(self._paths[0][0]._source_state)


class PartialParametricPathCollection(PathCollection):
    """
    Models a collection of paths which all diverge at the same point in the source code, and do not
    start at the beginning of the monitored function.
    """

    def __init__(self, paths, original_paths, path_parameters, scfg, function_name):
        PathCollection.__init__(self, paths, scfg, function_name, parametric=True)
        self._original_paths = original_paths
        self._path_parameters = path_parameters
        self._grammar = scfg.derive_grammar()

    def intersection(self):
        """
        Perform intersection, but such that the parse trees used
        are generated starting from the beginning of each path (we assume the paths
        start in the same place).
        """
        return super(PartialParametricPathCollection, self).intersection(self._paths[0][0]._source_state)

    def get_path_parameters(self):
        """
        Get the list of `path parameters`, which are objects that can be used internally to determine
        which subpath was taken by a given program path at a specific point in the program.
        """
        return self._path_parameters

    def get_subpaths_from_parameter(self, path_parameter):
        """
        Given a ``PathParameter`` object in ``path_parameter``, get the subpath given to it by this
        parametric path.
        """
        path_parameter = path_parameter.path
        parameter_values = []
        for path in self._original_paths:
            parse_tree = ParseTree(path, self._grammar, path[0]._source_state, parametric=True)
            subtree = parse_tree.get_parameter_subtree(path_parameter)
            subpath = subtree.read_leaves()
            parameter_values.append(subpath)

        return parameter_values


class ObservationCollection(object):
    """
    A collection of observation objects.  Defines methods for transformation to a ``PathCollection`` object.
    """

    def __init__(self, observations):
        self._observations = observations

    def to_paths(self, scfg):
        """
        Based on the relevant Symbolic Control-Flow Graph for the current collection of observations,
        reconstruct the paths up to each observation through the Symbolic Control-Flow Graph and return a
        ``PathCollection``.
        """

        connection = get_connection()

        # get the scfg of the function

        function_obj = function(
            function_call(
                verdict(
                    self._observations[0].verdict
                ).function_call
            ).function
        )

        function_name = function_obj.fully_qualified_name

        # get the path length of the instrumentation point of this
        # set of observations (assuming we deal with a single instrumentation point)

        reaching_path_length = instrumentation_point(
            self._observations[0].instrumentation_point
        ).reaching_path_length

        condition_sequences = []
        for observation in self._observations:
            result_dictionary = json.loads(
                connection.request("client/get_path_condition_sequence/%i/" % observation.id)
            )
            condition_sequence = result_dictionary["path_subchain"]

            #condition_sequence = map(deserialise_condition, condition_sequence)
            condition_sequences.append(condition_sequence)

        paths = []

        for condition_sequence in condition_sequences:
            reconstructed_path = edges_from_condition_sequence(scfg, condition_sequence, reaching_path_length)
            paths.append(reconstructed_path)

        return PathCollection(paths, scfg, function_name)
