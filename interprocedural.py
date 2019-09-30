"""
Module for inter-procedural analysis.
Prototype stage.
"""

def scfg_element_to_dot(scfg_obj):
	"""
	Gives a string that can be used by dot for drawing parse trees.
	"""
	return str(scfg_obj).replace("<", "").replace(">", "")

class CallTreeVertex(object):
	"""
	Models a vertex in a class tree.
	"""

	def __init__(self, tree, call_obj=None):
		self._call_obj = call_obj
		self._children = []
		tree._vertices.append(self)

	def __repr__(self):
		return "<CallTreeVertex (%s)>" % (self._call_obj)

	def add_child(self, vertex):
		self._children.append(vertex)

class CallTree(object):
	"""
	Models a graph structure derived from the list of calls that happened
	during a transaction/http request.
	Note: we have a tree because, even with recursion, vertices are calls, and not
	actual functions, so we cannot have cycles.
	"""

	def __init__(self, http_request):
		"""
		Given an HTTP request, get all calls that happened during it
		and construct a tree.
		"""

		self._vertices = []

		self._all_calls = http_request.get_calls()
		self._all_calls.sort(key=lambda call : call.time_of_call)

		# construct empty root
		self._root = CallTreeVertex(self)

		# construct the tree, starting at the empty root
		self.process_vertex(self._root, self._all_calls)

	def __repr__(self):
		return "<CallTree>"

	def process_vertex(self, root, calls):
		"""
		Given a root and a list of child calls,
		construct the subtree rooted here.
		"""

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
			callees = filter(lambda call : call.time_of_call < end_time, calls)

			# expand the subtree
			self.process_vertex(new_vertex, callees)

			# remove the calls we've just processed
			calls = list(set(calls) - set(callees))

	def write_to_file(self, file_name):
		"""
		Write this call tree to a dot file.
		"""
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