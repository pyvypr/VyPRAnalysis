import json
import requests
import urllib2
from datetime import datetime
import pickle
from graphviz import Digraph
#import matplotlib.pyplot as plt
#from VyPR import monitor_synthesis
#from flask import jsonify
import sys
import ast
sys.path.append("VyPR/")
from monitor_synthesis.formula_tree import *
from control_flow_graph.construction import *
#from control_flow_graph.parse_tree import ParseTree

#server_url is a global variable which can be changed by passing a string to the set_server() function
server_url=json.load(open('config.json'))["verdict_server_url"]
def set_server(given_url):
    global server_url
    server_url=given_url

#from VyPR-server/app/paths.py
def get_qualifier_subsequence(function_qualifier):
	"""
	Given a fully qualified function name, iterate over it and find the file
	in which the function is defined (this is the entry in the qualifier chain
	before the one that causes an import error)/
	"""

	# tokenise the qualifier string so we have names and symbols
	# the symbol used to separate two names tells us what the relationship is
	# a/b means a is a directory and b is contained within it
	# a.b means b is a member of a, so a is either a module or a class

	tokens = []
	last_position = 0
	for (n, character) in enumerate(list(function_qualifier)):
		if character in [".", "/"]:
			tokens.append(function_qualifier[last_position:n])
			tokens.append(function_qualifier[n])
			last_position = n + 1
		elif n == len(function_qualifier)-1:
			tokens.append(function_qualifier[last_position:])

	return tokens

#class function represents the table function in the database
#it is initialized by its name or id
#as f=function(id=1) or f=function(fully_qualified_name=name)
class function:
    def __init__(self, id=None, fully_qualified_name=None):
        if id==None and fully_qualified_name==None:
            raise ValueError('id or name of function needed as argument')
        if fully_qualified_name!=None:
            self.fully_qualified_name=fully_qualified_name
            str=urllib2.urlopen(server_url+'client/get_function_by_name/%s/' % fully_qualified_name).read()
            str=str[1:-1]
            f_dict=json.loads(str)
            self.id=f_dict["id"]
            self.property=f_dict["property"]
        elif id!=None:
            self.id=id
            str=urllib2.urlopen(server_url+'client/get_function_by_id/%d/' % id).read()
            str=str[1:-1]
            f_dict=json.loads(str)
            self.fully_qualified_name=f_dict["fully_qualified_name"]
            self.property=f_dict["property"]

    #function.get_calls() returns a list of calls for the given function
    #if given the optional parameter value, it returns the list of the
    #function calls which happened during the given http_request
    def get_calls(self, request=None):
        if request==None:
            str=urllib2.urlopen(server_url+'client/list_function_calls_f/%s/'% self.fully_qualified_name).read()
        else:
            str=urllib2.urlopen(server_url+'client/list_function_calls_http_id/%d/%d/'%(request.id,self.id)).read()
        calls_dict=json.loads(str)
        calls_list=[]
        for call in calls_dict:
            call_class=function_call(call["id"],call["function"],call["time_of_call"],call["http_request"])
            calls_list.append(call_class)
        return calls_list
    def get_calls_with_failed_verdict(self):
        str=urllib2.urlopen(server_url+'client/list_function_calls_failed_verdict/%d/'%(self.id)).read()
        calls_dict=json.loads(str)
        calls_list=[]
        for call in calls_dict:
            call_class=function_call(call["id"],call["function"],call["time_of_call"],call["http_request"])
            calls_list.append(call_class)
        return calls_list
    def get_graph(self):
        #returns scfg of function
        func=self.fully_qualified_name
        location=json.load(open('config.json'))["monitored_service"]
        module = func[0:func.rindex(".")]
    	func = func[func.rindex(".")+1:]
    	file_name = module.replace(".", "/") + ".py.inst"
    	file_name_without_extension = module.replace(".", "/")
    	# extract asts from the code in the file
    	code = "".join(open(os.path.join(location, file_name), "r").readlines())
    	asts = ast.parse(code)
    	print(asts.body)
    	qualifier_subsequence = get_qualifier_subsequence(func)
    	function_name = func.split(".")
    	# find the function definition
    	print("finding function/method definition using qualifier chain %s" % function_name)
    	actual_function_name = function_name[-1]
    	hierarchy = function_name[:-1]
    	print(actual_function_name, hierarchy)
    	current_step = asts.body
    	# traverse sub structures
    	for step in hierarchy:
    		current_step = filter(lambda entry : (type(entry) is ast.ClassDef and entry.name == step),current_step)[0]
    	# find the final function definition
    	function_def = filter(lambda entry : (type(entry) is ast.FunctionDef and entry.name == actual_function_name),current_step.body if type(current_step) is ast.ClassDef else current_step)[0]
    	# construct the scfg of the code inside the function
    	scfg = CFG()
    	scfg_vertices = scfg.process_block(function_def.body)
    	return scfg

class property:
    def __init__(self, hash, serialised_structure=None):
        self.hash=hash
        if serialised_structure==None:
            str=urllib2.urlopen(server_url+'client/get_property_by_hash/%s/' % hash).read()
            if str=="None":
                raise ValueError('no such property')
            else:
                str=str[1:-1]
                f_dict=json.loads(str)
                self.serialised_structure=f_dict["serialised_structure"]
        else:
            self.serialised_structure=serialised_structure

class binding:
  def __init__(self,id,binding_space_index=None,function=None,binding_statement_lines=None):
    self.id=id
    if binding_space_index==None or function==None or binding_statement_lines==None:
        str=urllib2.urlopen(server_url+'client/get_binding_by_id/%d/' % id).read()
        if str=="None": raise ValueError('there is no binding with given id')
        str=str[1:-1]
        dict=json.loads(str)
        self.binding_space_index=dict["binding_space_index"]
        self.function=dict["function"]
        self.binding_statement_lines=dict["binding_statement_lines"]
    else:
        self.binding_space_index=binding_space_index
        self.function=function
        self.binding_statement_lines=binding_statement_lines

#class function_call represents the homonymous table in the database
#initialized by either just the id or all the values
class function_call:
    def __init__(self,id,function=None,time_of_call=None,http_request=None):
        self.id=id
        if function==None or time_of_call==None or http_request==None:
            str=urllib2.urlopen(server_url+'client/get_call_by_id/%d/' % id).read()
            str=str[1:-1]
            dict=json.loads(str)
            self.function=dict["function"]
            self.time_of_call=dict["time_of_call"]
            self.http_request=dict["http_request"]
        else:
            self.function=function
            self.time_of_call=time_of_call
            self.http_request=http_request
    def first_observation_fail(self):
        #returns the first (wrt verdicts) observation that causes failure for the given call
        str=urllib2.urlopen(server_url+'client/first_observation_of_call_fail/%d/' % self.id).read()
        if str=="None":
            print("no such objects")
            return
        str=str[1:-1]
        d=json.loads(str)
        return observation(id=d["id"],instrumentation_point=d["instrumentation_point"],verdict=d["verdict"],observed_value=d["observed_value"],atom_index=d["atom_index"],previous_condition=d["previous_condition"])
    def get_verdicts(self):
        str=urllib2.urlopen(server_url+'client/list_verdicts_of_call/%d/'% self.id).read()
        if str=="None": print('no verdicts for given function call')
        verdicts_dict=json.loads(str)
        verdicts_list=[]
        for v in verdicts_dict:
            verdict_class=verdict(v["id"],v["binding"],v["verdict"],v["time_obtained"],v["function_call"],v["collapsing_atom"])
            verdicts_list.append(verdict_class)
        return verdicts_list
    def get_observations(self):
        str=urllib2.urlopen(server_url+'client/list_observations_during_call/%d/'% self.id).read()
        if str=="None": print('no observations for given function call')
        obs_dict=json.loads(str)
        obs_list=[]
        for o in obs_dict:
            obs_class=observation(o["id"],o["instrumentation_point"],o["verdict"],o["observed_value"],o["atom_index"],o["previous_condition"])
            obs_list.append(obs_class)
        return obs_list

#class verdict has same objects as the table verdict in the database
#initialized by either just the id or all the values
#function verdict.get_atom() returns the atom which the given verdict concerns
class verdict:
    def __init__(self,id,binding=None,verdict=None,time_obtained=None,function_call=None,collapsing_atom=None):
        self.id=id
        if binding==None:
            str=urllib2.urlopen(server_url+'client/get_verdict_by_id/%d/' % self.id).read()
            str=str[1:-1]
            d=json.loads(str)
            self.binding=d["binding"]
            self.verdict=d["verdict"]
            self.time_obtained=d["time_obtained"]
            self.function_call=d["function_call"]
            self.collapsing_atom=d["collapsing_atom"]
        else:
            self.binding=binding
            self.verdict=verdict
            self.time_obtained=time_obtained
            self.function_call=function_call
            self.collapsing_atom=collapsing_atom
    def get_atom(self):
        return atom(index_in_atoms=self.collapsing_atom)

def list_verdicts_with_value(value):
    #called as list_verdicts(True) or list_verdicts(False)
    #returns a list of objects 'class verdict' with the given value
    str=urllib2.urlopen(server_url+'client/list_verdicts_with_value/%d/' % value).read()
    if str=="None": raise ValueError('there are no such verdicts')
    verdicts_dict=json.loads(str)
    verdicts_list=[]
    for v in verdicts_dict:
        verdict_class=verdict(v["id"],v["binding"],v["time_obtained"],v["function_call"],v["collapsing_atom"])
        verdicts_list.append(verdict_class)
    return verdicts_list

def list_verdicts_dict_with_value(value):
    #finds all verdicts in the database with given value
    #returns a dictionary with keys:
    #from verdict - id, binding, verdict, time_obtained,
    #from function_call - function, time_of_call
    #from function - fully_qualified_name, property
    str=urllib2.urlopen(server_url+'client/list_verdicts_function_property_by_value/%d/' % value).read()
    if str=="None": raise ValueError('there are no such verdicts')
    d=json.loads(str)
    return d

#class http_request represents the http_request table in the database
#initialized as http_request(id=1) or http_request(time_of_request=t)
class http_request:
    def __init__(self, id=None, time_of_request=None):
        if id!=None:
            self.id=id
            if time_of_request==None:
                str=urllib2.urlopen(server_url+'client/get_http_by_id/%d/' % self.id).read()
                str=str[1:-1]
                d=json.loads(str)
                self.time_of_request=d["time_of_request"]
            else:
                self.time_of_request=time_of_request
        elif time_of_request!=None:
            self.time_of_request=time_of_request
            str=urllib2.urlopen(server_url+'client/get_http_by_time/%s/' % self.time_of_request).read()
            str=str[1:-1]
            d=json.loads(str)
            self.id=d["id"]
        else:
            raise ValueError('either id or time_of_request argument required')
    def get_calls(self):
        str=urllib2.urlopen(server_url+'client/list_function_calls_http/%d/'% self.id).read()
        if str=="None":
            print('no calls during the given request')
            return
        calls_dict=json.loads(str)
        calls_list=[]
        for call in calls_dict:
            call_class=function_call(call["id"],call["function"],call["time_of_call"],call["http_request"])
            calls_list.append(call_class)
        return calls_list

#initialized as either atom(id=n) or atom(index_in_atoms=n) or with all arguments if known
class atom:
    def __init__(self,id=None,property_hash=None,serialised_structure=None,index_in_atoms=None):
        if id!=None and property_hash!=None and serialised_structure!=None and index_in_atoms!=None:
            self.id=id
            self.property_hash=property_hash
            self.serialised_structure=serialised_structure
            self.index_in_atoms=index_in_atoms
        else:
            if id!=None:
                self.id=id
                str=urllib2.urlopen(server_url+'client/get_atom_by_id/%d/' % self.id).read()
                str=str[1:-1]
                d=json.loads(str)
                self.property_hash=d["property_hash"]
                self.serialised_structure=d["serialised_structure"]
                self.index_in_atoms=d["index_in_atoms"]
            elif index_in_atoms!=None:
                self.index_in_atoms=index_in_atoms
                str=urllib2.urlopen(server_url+'client/get_atom_by_index/%d/' % self.index_in_atoms).read()
                str=str[1:-1]
                d=json.loads(str)
                self.property_hash=d["property_hash"]
                self.serialised_structure=d["serialised_structure"]
                self.id=d["id"]
            else:
                raise ValueError('either id or index_in_atoms argument needed to initialize object')
    def get_structure(self):
        #atom.get_structure() returns the serialised structure of the atom in decoded format
        str=self.serialised_structure
        obj=pickle.loads(str)
        return obj

#the idea is to list all atoms for which verdict is ture or false, is it even useful?
def get_atom_list(verdict_value):
    str=urllib2.urlopen(server_url+'client/list_atoms_where_verdict/%d/'% verdict_value).read()
    if str=="None":
        print('there are no verdicts with given value')
        return
    atoms_dict=json.loads(str)
    atoms_list=[]
    for atom_elem in atoms_dict:
        atom_class=atom(atom_elem["id"],atom_elem["property_hash"],atom_elem["serialised_structure"],atom_elem["index_in_atoms"])
        atoms_list.append(atom_class)
    return atoms_list

class atom_instrumentation_point_pair:
    def __init__(self,atom,instrumentation_point):
        self.atom=atom
        self.instrumentation_point=instrumentation_point

class binding_instrumentation_point_pair:
    def __init__(self,binding,instrumentation_point):
        self.binding=binding
        self.instrumentation_point=instrumentation_point

class instrumentation_point:
    def __init__(self,id,serialised_condition_sequence=None,reaching_path_length=None):
        self.id=id
        if serialised_condition_sequence==None or reaching_path_length==None:
            str=urllib2.urlopen(server_url+'client/get_instrumentation_point_by_id/%d/' % self.id).read()
            if str=="None":
                raise ValueError("there is no instrumentation point with given id")
            else:
                str=str[1:-1]
                d=json.loads(str)
                self.serialised_condition_sequence=d["serialised_condition_sequence"]
                self.reaching_path_length=d["reaching_path_length"]
        else:
            self.serialised_condition_sequence=serialised_condition_sequence
            self.reaching_path_length=reaching_path_length
    def get_observations(self):
        str=urllib2.urlopen(server_url+'client/list_observations_of_point/%d/'% self.id).read()
        if str=="None":
            print('no observations for given instrumentation point')
            return
        obs_dict=json.loads(str)
        obs_list=[]
        for o in obs_dict:
            obs_class=observation(o["id"],o["instrumentation_point"],o["verdict"],o["observed_value"],o["atom_index"],o["previous_condition"])
            obs_list.append(obs_class)
        return obs_list

class observation:
    def __init__(self,id,instrumentation_point=None,verdict=None,observed_value=None,atom_index=None,previous_condition=None):
        self.id=id
        if instrumentation_point==None or verdict==None or observed_value==None or atom_index==None or previous_condition==None:
            str=urllib2.urlopen(server_url+'client/get_observation_by_id/%d/' % self.id).read()
            if str=="None": raise ValueError('there is no observation with given id')
            str=str[1:-1]
            d=json.loads(str)
            self.instrumentation_point=d["instrumentation_point"]
            self.verdict=d["verdict"]
            self.observed_value=d["observed_value"]
            self.atom_index=d["atom_index"]
            self.previous_condition=d["previous_condition"]
        else:
            self.instrumentation_point=instrumentation_point
            self.verdict=verdict
            self.observed_value=observed_value
            self.atom_index=atom_index
            self.previous_condition=previous_condition
    def get_assignments(self):
        str=urllib2.urlopen(server_url+'client/list_assignments_given_observation/%d/'% self.id).read()
        if str=="None": raise ValueError('no assignments paired with given observation')
        assignment_dict=json.loads(str)
        assignment_list=[]
        for a in assignment_dict:
            assignment_class=assignment(a["id"],a["variable"],a["value"],a["type"])
            assignment_list.append(assignment_class)
        return assignment_list
    def get_assignments_as_dictionary(self):
        str=urllib2.urlopen(server_url+'client/get_assignment_dict_from_observation/%d/'% self.id).read()
        if str=="None": raise ValueError('no assignments paired with given observation')
        assignment_dict=json.loads(str)
        for a in assignment_dict:
            # TODO: use assignment_dict[a][1] to decide if we need to import another type
            assignment_dict[a] = pickle.loads(assignment_dict[a][0])
        return assignment_dict
    def verdict_severity(self):
        formula=atom(index_in_atoms=self.atom_index).get_structure()
        interval=formula._interval
        lower=interval[0]
        upper=interval[1]
        x=float(self.observed_value)
        #d is the distance from observed value to the nearest interval bound
        d=min(abs(x-lower),abs(x-upper))
        #sign=-1 if verdict value=0 and sign=1 if verdict is true
        sign=-1+2*(formula.check(x))
        return sign*d

def verdict_severity(obs):
    return obs.verdict_severity()

class observation_assignment_pair:
    def __init__(self,observation,assignment):
        self.observation=observation
        self.assignment=assignment

class assignment:
    def __init__(self,id,variable=None,value=None,type=None):
        self.id=id
        if variable==None or value==None or type==None:
            str=urllib2.urlopen(server_url+'client/get_assignment_by_id/%d/' % self.id).read()
            if str=="None": raise ValueError('there is no assignment with given id')
            str=str[1:-1]
            d=json.loads(str)
            self.variable=d["variable"]
            self.value=d["value"] #is it better to keep this serialised or to deserialise it?
            self.type=d["type"]
        else:
            self.variable=variable
            self.value=value
            self.type=type

class path_condition_structure:
    def __init__(self,id,serialised_condition=None):
        self.id=id
        if serialised_condition==None:
            str=urllib2.urlopen(server_url+'client/get_path_condition_structure_by_id/%d/' % self.id).read()
            if str=="None": raise ValueError('there is no path condition structure with given id')
            str=str[1:-1]
            d=json.loads(str)
            self.serialised_condition=d["serialised_condition"]
        else:
            self.serialised_condition=serialised_condition

class path_condition:
    def __init__(self,id,serialised_condition=None,next_path_condition=None,function_call=None):
        self.id=id
        if serialised_condition==None or next_path_condition==None or function_call==None:
            str=urllib2.urlopen(server_url+'client/get_path_condition_by_id/%d/' % self.id).read()
            if str=="None": raise ValueError('there is no path condition with given id')
            str=str[1:-1]
            d=json.loads(str)
            self.serialised_condition=d["serialised_condition"]
            self.next_path_condition=d["next_path_condition"]
            self.function_call=d["function_call"]
        else:
            self.serialised_condition=serialised_condition
            self.next_path_condition=next_path_condition
            self.function_call=function_call

class search_tree:
    def __init__(self,id,root_vertex=None,instrumentation_point=None):
        self.id=id
        if root_vertex==None or instrumentation_point==None:
            str=urllib2.urlopen(server_url+'client/get_search_tree_by_id/%d/' % self.id).read()
            if str=="None": raise ValueError('there is no search tree with given id')
            str=str[1:-1]
            d=json.loads(str)
            self.root_vertex=d["root_vertex"]
            self.instrumentation_point=d["instrumentation_point"]
        else:
            self.root_vertex=root_vertex
            self.instrumentation_point=instrumentation_point

class search_tree_vertex:
    def __init__(self,id,observation=None,intersection=None,parent_vertex=None):
        self.id=id
        if observation==None or intersection==None or parent_vertex==None:
            str=urllib2.urlopen(server_url+'client/get_search_tree_vertex_by_id/%d/' % self.id).read()
            if str=="None": raise ValueError('there is no search tree vertex with given id')
            str=str[1:-1]
            d=json.loads(str)
            self.observation=d["observation"]
            self.intersection=d["intersection"]
            self.parent_vertex=d["parent_vertex"]
        else:
            self.observation=observation
            self.intersection=intersection
            self.parent_vertex=parent_vertex

class intersection:
    def __init__(self,id,condition_sequence_string=None):
        self.id=id
        if condition_sequence_string==None:
            str=urllib2.urlopen(server_url+'client/get_intersection_by_id/%d/' % self.id).read()
            if str=="None": raise ValueError('there is no intersection with given id')
            str=str[1:-1]
            d=json.loads(str)
            self.condition_sequence_string=d["condition_sequence_string"]
        else:
            self.condition_sequence_string=condition_sequence_string

def write_scfg(scfg_object,file_name):
    graph = Digraph()
    graph.attr("graph", splines="true", fontsize="10")
    shape = "rectangle"
    for vertex in scfg_object.vertices:
        graph.node(str(id(vertex)), str(vertex._name_changed), shape=shape)
        for edge in vertex.edges:
            graph.edge(str(id(vertex)),	str(id(edge._target_state)),"%s - %s - path length = %s" % (str(edge._operates_on) if not(type(edge._operates_on[0]) is ast.Print) else "print stmt",edge._condition,str(edge._target_state._path_length)))
    graph.render(file_name)
    print("Writing SCFG to file '%s'." % file_name)

def list_observations():
    str=urllib2.urlopen(server_url+'client/list_observations/').read()
    if str=="None":
        print('no observations')
        return
    obs_dict=json.loads(str)
    obs_list=[]
    for o in obs_dict:
        obs_class=observation(o["id"],o["instrumentation_point"],o["verdict"],o["observed_value"],o["atom_index"],o["previous_condition"])
        obs_list.append(obs_class)
    return obs_list
