"""
Module for path reconstruction in the analysis library.
"""

import pickle
import sys
import json

from VyPRAnalysis import get_connection

from VyPR.monitor_synthesis.formula_tree import LogicalNot

def edges_from_condition_sequence(scfg, path_subchain, instrumentation_point_path_length):
	"""
	Given a sequence of (deserialised) conditions in path_subchain and the final path length,
	reconstruct a path through the scfg, including loop multiplicity.
	"""
	#print("reconstruction with path subchain %s" % str(path_subchain))
	condition_index = 0
	curr = scfg.starting_vertices
	#path = [curr]
	path = []
	cumulative_conditions = []
	while condition_index < len(path_subchain):
		#path.append(curr)
		#print(curr._name_changed)
		if len(curr.edges) > 1:
			# more than 1 outgoing edges means we have a branching point

			#TODO: need to handle parameters in condition sequences
			if path_subchain[condition_index] == "parameter":
				if curr._name_changed == ["conditional"]:
					# add the vertex to the path, skip past the construct
					# and increment the condition index
					path.append(curr)
					curr = curr.post_conditional_vertex
					condition_index += 1
					continue

			# we have to decide whether it's a loop or a conditional
			if curr._name_changed == ["conditional"]:
				#print("traversing conditional %s with condition %s" % (curr, path_subchain[condition_index]))
				# path_subchain[condition_index] is the index of the branch to follow if we're dealing with a conditional
				path.append(curr.edges[path_subchain[condition_index]])
				curr = curr.edges[path_subchain[condition_index]]._target_state
				condition_index += 1
			elif curr._name_changed == ["loop"]:
				#print("traversing loop %s with condition %s" % (curr, path_subchain[condition_index]))
				if path_subchain[condition_index] == "enter-loop":
					#print("finding edge entering the loop")
					# condition isn't a negation, so follow the edge leading into the loop
					for edge in curr.edges:
						#print(edge._condition)
						if edge._condition == ["enter-loop"]:
							#print("traversing edge with positive loop condition")
							cumulative_conditions.append("for")
							# follow this edge
							curr = edge._target_state
							path.append(edge)
							break
					# make sure the next branching point consumes the next condition in the chain
					condition_index += 1
				else:
					#print("finding edge skipping the loop")
					# go straight past the loop
					for edge in curr.edges:
						if edge._condition == ["end-loop"]:
							#print("traversing edge with negative loop condition")
							cumulative_conditions.append(edge._condition)
							# follow this edge
							curr = edge._target_state
							path.append(edge)
							break
					# make sure the next branching point consumes the next condition in the chain
					condition_index += 1
			elif curr._name_changed == ["try-catch"]:
				#print("traversing try-catch")
				# for now assume that we immediately traverse the no-exception branch
				#print(curr)
				# search the outgoing edges for the edge leading to the main body
				for edge in curr.edges:
					#print("testing edge with condition %s against cumulative condition %s" %\
					#		(edge._condition, cumulative_conditions + [path_subchain[condition_index]]))
					if edge._condition[-1] == "try-catch-main":
						#print("traversing edge with condition %s" % edge._condition)
						curr = edge._target_state
						path.append(edge)
						cumulative_conditions.append(edge._condition[-1])
						break
				condition_index += 1
			else:
				# probably the branching point at the end of a loop - currently these aren't explicitly marked
				# the behaviour here with respect to consuming branching conditions will be a bit different
				if path_subchain[condition_index] == "enter-loop":
					# go back to the start of the loop without consuming the condition
					#print("going back around the loop from last instruction")
					relevant_edge = filter(lambda edge : edge._condition == 'loop-jump', curr.edges)[0]
					curr = relevant_edge._target_state
					path.append(relevant_edge)
				else:
					# go past the loop
					#print(curr.edges)
					#print("ending loop from last instruction")
					relevant_edge = filter(lambda edge : edge._condition == 'post-loop', curr.edges)[0]
					curr = relevant_edge._target_state
					path.append(relevant_edge)
					# consume the negative condition
					condition_index += 1

			#print("condition index %i from condition chain length %i" % (condition_index, len(path_subchain)))
		elif curr._name_changed == ["post-conditional"]:
			#print("traversing post-conditional")
			# check the next vertex - if it's also a post-conditional, we move to that one but don't consume the condition
			# if the next vertex isn't a post-conditional, we consume the condition and move to it
			if curr.edges[0]._target_state._name_changed != ["post-conditional"]:
				# consume the condition
				condition_index += 1
			path.append(curr.edges[0])
			curr = curr.edges[0]._target_state
			#print("resulting state after conditional is %s" % curr)
			#print("condition index %i from condition chain length %i" % (condition_index, len(path_subchain)))
		elif curr._name_changed == ["post-loop"]:
			#print("traversing post-loop")
			# condition is consumed when branching at the end of the loop is detected, so no need to do it here
			#print("adding %s outgoing from %s to path" % (curr.edges[0], curr))
			path.append(curr.edges[0])
			curr = curr.edges[0]._target_state
			#print("condition index %i from condition chain length %i" % (condition_index, len(path_subchain)))
		elif curr._name_changed == ["post-try-catch"]:
			#print("traversing post-try-catch")
			if curr.edges[0]._target_state._name_changed != ["post-try-catch"]:
				# consume the condition
				condition_index += 1
			path.append(curr.edges[0])
			curr = curr.edges[0]._target_state
			#print("condition index %i from condition chain length %i" % (condition_index, len(path_subchain)))
		else:
			#print("no branching at %s" % curr)
			path.append(curr.edges[0])
			curr = curr.edges[0]._target_state
			#print("condition index %i from condition chain length %i" % (condition_index, len(path_subchain)))

	#print("finishing path traversal with path length %i" % instrumentation_point_path_length)

	# traverse the remainder of the branch using the path length of the instrumentation point
	# that generated the observation we're looking at
	#print("starting remainder of traversal from vertex %s" % curr)
	limit = instrumentation_point_path_length-1 if len(path_subchain) > 0 else instrumentation_point_path_length
	for i in range(limit):
		#path.append(curr)
		path.append(curr.edges[0])
		curr = curr.edges[0]._target_state

	#path.append(curr)

	return path


def deserialise_condition(serialised_condition):
	if serialised_condition != "":
		if not(serialised_condition in ["loop-jump", "conditional exited", "try-catch exited", "try-catch-main", "parameter", "exit conditional"]):
			#print(serialised_condition)
			unserialised_condition = pickle.loads(serialised_condition)
		else:
			unserialised_condition = serialised_condition
	else:
		unserialised_condition = None
	return unserialised_condition
