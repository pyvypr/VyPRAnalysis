"""
Base ORM classes.
"""
import json
import os
import ast
import pickle

# VyPRAnalysis imports
from VyPRAnalysis import get_server, get_connection, get_monitored_service_path
from VyPRAnalysis.utils import get_qualifier_subsequence
from VyPRAnalysis.path_reconstruction import edges_from_condition_sequence, deserialise_condition

# VyPR imports
import VyPR.control_flow_graph.construction

class Function(object):

    def __init__(self, id, fully_qualified_name, property):
        self.id = id
        self.fully_qualified_name = fully_qualified_name
        self.property = property

    def __repr__(self):
        return "<%s id=%i, fully_qualified_name=%s, property=%s>" %\
            (
                self.__class__.__name__,
                self.id,
                self.fully_qualified_name,
                self.property
            )

    def get_calls(self, request=None):
        """function.get_calls() returns a list of calls for the given function
        if given the optional parameter value, it returns the list of the
        function calls which happened during the given http_request"""
        connection = get_connection()
        if request==None:
            str=connection.request('client/list_function_calls_f/%s/'% self.fully_qualified_name)
        else:
            str=connection.request('client/list_function_calls_http_id/%d/%d/'%(request.id,self.id))
        if (str=="None"): raise ValueError('no such calls')
        calls_dict=json.loads(str)
        calls_list=[]
        for call in calls_dict:
            call_class=FunctionCall(call["id"],call["function"],call["time_of_call"], call["end_time_of_call"],call["http_request"])
            calls_list.append(call_class)
        return calls_list

    def get_calls_with_verdict(self, verdict_value):
        connection = get_connection()
        str=connection.request('client/list_function_calls_with_verdict/%d/%d/'%(self.id,verdict_value))
        if str=="None":raise ValueError('no such calls')
        calls_dict=json.loads(str)
        calls_list=[]
        for call in calls_dict:
            call_class=FunctionCall(call["id"],call["function"],call["time_of_call"], call["end_time_of_call"],call["http_request"])
            calls_list.append(call_class)
        return calls_list

    def get_graph(self):
        """returns scfg of function"""
        func=self.fully_qualified_name
        location=get_monitored_service_path()
        module = func[0:func.rindex(".")]
    	func = func[func.rindex(".")+1:]
    	file_name = module.replace(".", "/") + ".py.inst"
    	file_name_without_extension = module.replace(".", "/")
    	# extract asts from the code in the file
    	code = "".join(open(os.path.join(location, file_name), "r").readlines())
    	asts = ast.parse(code)
    	print(asts.body)
    	qualifier_subsequence = get_qualifier_subsequence(func)
	func = func.replace(":", ".")
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
    	scfg = VyPR.control_flow_graph.construction.CFG()
    	scfg_vertices = scfg.process_block(function_def.body)
    	return scfg

    def get_verdicts(self, verdict_value=None):
        connection = get_connection()
        if verdict_value==None:
            str=connection.request('client/list_verdicts_of_function/%d/'%self.id)
        else:
            str=connection.request('client/list_verdicts_of_function_with_value/%d/%d/'%(self.id,verdict_value))
        if str=="None":raise ValueError('no such verdicts')
        verdicts_dict=json.loads(str)
        verdicts_list=[]
        for v in verdicts_dict:
            verdict_class=verdict(v["id"],v["binding"],v["verdict"],v["time_obtained"],v["function_call"])
            verdicts_list.append(verdict_class)
        return verdicts_list

    def get_bindings(self):
        connection = get_connection()
        result = connection.request("client/get_bindings_from_function_property_pair/%d/" % self.id)
        if result == "None":
            raise ValueError("No such bindings")
        bindings_dict = json.loads(result)
        binding_list = []
        for b in bindings_dict:
            binding_obj = binding(b["id"], b["binding_space_index"], b["function"], b["binding_statement_lines"])
            binding_list.append(binding_obj)

        return binding_list

def function(id=None, fully_qualified_name=None, property=None):
    """
    Factory function for either getting a single function, or a list of functions.
    """

    connection = get_connection()

    if id!=None and fully_qualified_name!=None and property!=None:

        return Function(
            id=id,
            fully_qualified_name=fully_qualified_name,
            property=property
        )

    elif fully_qualified_name!=None:

        functions=connection.request('client/get_function_by_name/%s/' % fully_qualified_name)
        if functions=="None": raise ValueError('no functions named %s'%fully_qualified_name)
        f_dict=json.loads(functions)
        functions_list = []

        for f in f_dict:
            f_obj = function(f["id"], f["fully_qualified_name"], f["property"])
            functions_list.append(f_obj)

        return functions_list

    elif id!=None:

        str=connection.request('client/get_function_by_id/%d/' % id)
        if str=="None": raise ValueError('no functions with given ID')
        str=str[1:-1]
        f_dict=json.loads(str)

        return Function(
            id=id,
            fully_qualified_name=f_dict["fully_qualified_name"],
            property=f_dict["property"]
        )


class Property(object):
    def __init__(self, hash):
        connection = get_connection()
        self.hash=hash
        str=connection.request('client/get_property_by_hash/%s/' % hash)
        if str=="None":
            raise ValueError('no such property')
        else:
            str=str[1:-1]
            f_dict=json.loads(str)
            self.serialised_structure=f_dict["serialised_structure"]

    def __repr__(self):
        return "<Property hash=%s>" % self.hash

class Binding(object):
    def __init__(self,id,binding_space_index,function,binding_statement_lines):
        connection = get_connection()
        self.id=id
        if binding_space_index==None or function==None or binding_statement_lines==None:
            pass
        else:
            self.binding_space_index=binding_space_index
            self.function=function
            self.binding_statement_lines=binding_statement_lines

    def __repr__(self):
        return "<%s id=%i, binding_space_index=%i, function=%i, binding_statement_lines=%s>" %\
            (
                self.__class__.__name__,
                self.id,
                self.binding_space_index,
                self.function,
                self.binding_statement_lines
            )

    def get_verdicts(self):
        connection = get_connection()
        str=connection.request('client/list_verdicts_from_binding/%s/' % self.id)
        if str=="None":
            raise ValueError('no such property')
        else:
            #str=str[1:-1]
            f_dict=json.loads(str)
            self.serialised_structure=f_dict["serialised_structure"]


def binding(id=None, binding_space_index=None, function=None, binding_statement_lines=None):

    connection = get_connection()

    if id!=None and binding_space_index!=None and function!=None and binding_statement_lines!=None:

        return Binding(
            id=id,
            binding_space_index=binding_space_index,
            function=function,
            binding_statement_lines=binding_statement_lines
        )

    elif id!=None:
        str=connection.request('client/get_binding_by_id/%d/' % id)
        if str=="None": raise ValueError('there is no binding with given id')
        str=str[1:-1]
        dict=json.loads(str)

        return Binding(
            id=id,
            binding_space_index=dict["binding_space_index"],
            function=dict["function"],
            binding_statement_lines=dict["binding_statement_lines"]
        )

    elif function!=None:

        bindings = connection.request("client/get_bindings_from_function_property_pair/%d/" % function)
        result = json.loads(bindings)
        binding_list = []
        for b in result:
            new_binding = binding(b["id"], b["binding_space_index"], b["function"], b["binding_statement_lines"])
            binding_list.append(new_binding)

        return binding_list

    else:

        raise Exception("Cannot instantiate single or multiple bindings with parameters given.")


class FunctionCall(object):
    """class function_call represents the homonymous table in the database
    initialized by either just the id or all the values"""

    def __init__(self,id,function,time_of_call,end_time_of_call,http_request):
        self.id=id
        self.function=function
        self.time_of_call=time_of_call
        self.end_time_of_call=end_time_of_call
        self.http_request=http_request

    def __repr__(self):
        return "<%s id=%i, function=%i, time_of_call=%s, end_time_of_call=%s, http_request=%i>" %\
            (
                self.__class__.__name__,
                self.id,
                self.function,
                self.time_of_call,
                self.end_time_of_call,
                self.http_request
            )

    def get_falsifying_observation(self):
        """returns the first (wrt verdicts) observation that causes
        failure for the given call"""

        connection = get_connection()

        str=connection.request('client/get_falsifying_observation_for_call/%d/' % self.id)
        if str=="None":
            print("no such objects")
            return
        str=str[1:-1]
        d=json.loads(str)
        return observation(id=d["id"],instrumentation_point=d["instrumentation_point"],verdict=d["verdict"],observed_value=d["observed_value"],atom_index=d["atom_index"],previous_condition=d["previous_condition"])

    def get_verdicts(self,value=None):
        connection = get_connection()
        if value==None:
            str=connection.request('client/list_verdicts_of_call/%d/'% self.id)
        else:
            str=connection.request('client/list_verdicts_with_value_of_call/%d/%d/'% (self.id,value))

        if str=="None": print('no verdicts for given function call')

        verdicts_dict=json.loads(str)
        verdicts_list=[]
        for v in verdicts_dict:
            verdict_class=verdict(v["id"],v["binding"],v["verdict"],v["time_obtained"],v["function_call"],v["collapsing_atom"])
            verdicts_list.append(verdict_class)
        return verdicts_list

    def get_observations(self):
        connection = get_connection()
        str=connection.request('client/list_observations_during_call/%d/'% self.id)
        if str=="None": print('no observations for given function call')
        obs_dict=json.loads(str)
        obs_list=[]
        for o in obs_dict:
            obs_class=observation(o["id"],o["instrumentation_point"],o["verdict"],o["observed_value"],o["atom_index"],o["previous_condition"])
            obs_list.append(obs_class)
        return obs_list

def function_call(id):
    """
    Factory function for function calls.
    The only way this needs to be used is with the ID of the function call.
    Otherwise, methods on other ORM objects can be used.
    """

    connection = get_connection()

    str=connection.request('client/get_call_by_id/%d/' % id)
    if str=="None": raise ValueError('no function calls with given ID')
    str=str[1:-1]
    dict=json.loads(str)

    return FunctionCall(
        id=id,
        function=dict["function"],
        time_of_call=dict["time_of_call"],
        end_time_of_call=dict["end_time_of_call"],
        http_request=dict["http_request"]
    )

class Verdict(object):
    """class verdict has the same objects as the table verdict in the database
    initialized by either just the id or all the values
    function verdict.get_atom() returns the atom which the given verdict concerns"""
    def __init__(self,id,binding=None,verdict=None,time_obtained=None,function_call=None,collapsing_atom=None):
        connection = get_connection()
        self.id=id
        if binding==None:
            str=connection.request('client/get_verdict_by_id/%d/' % self.id)
            if str=="None": raise ValueError('no verdicts with given ID')
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
            if collapsing_atom!=None: self.collapsing_atom=collapsing_atom

    def __repr__(self):
        return "<%s id=%i, binding=%i, verdict=%i, time_obtained=%s, function_call=%i, collapsing_atom=%i>" %\
            (
                self.__class__.__name__,
                self.id,
                self.binding,
                self.verdict,
                self.time_obtained,
                self.function_call,
                self.collapsing_atom
            )

    def get_property_hash(self):
        """
        initialise the binding using the attribute that stores its id
        initialise the function using the attribute of binding that stores function id
        finally, get the property which is an attribute of function
        """

        #it's possible to define a separate function for each of these steps
        #the code would be more straightforward then
        #or a database query that returns the property direcrtly (more efficient)
        return function(binding(self.binding).function).property

    def get_collapsing_atom(self):
        return Atom(index_in_atoms=self.collapsing_atom,property_hash=self.get_property_hash())

    def get_observations(self):
        """
        Get a list of the observations that were needed to obtain this verdict.
        """
        connection = get_connection()
        str=connection.request('client/get_observations_from_verdict/%d/'% self.id)
        if str=="None": print('no observations for given verdict')
        obs_dict=json.loads(str)
        obs_list=[]
        for o in obs_dict:
            obs_class=observation(o["id"],o["instrumentation_point"],o["verdict"],o["observed_value"],o["atom_index"],o["previous_condition"])
            obs_list.append(obs_class)
        return obs_list

def verdict(id=None, binding=None,verdict=None,time_obtained=None,function_call=None,collapsing_atom=None):
    """
    Factory function for verdicts.
    """

    connection = get_connection()

    if id!=None and binding!=None and verdict!=None and time_obtained!=None and function_call!=None and collapsing_atom!=None:

        return Verdict(
            id=id,
            binding=binding,
            verdict=verdict,
            time_obtained=time_obtained,
            function_call=function_call,
            collapsing_atom=collapsing_atom
        )

    elif id!=None:

        str=connection.request('client/get_verdict_by_id/%d/' % id)
        if str=="None": raise ValueError('no verdicts with given ID')
        str=str[1:-1]
        d=json.loads(str)

        return Verdict(
            id=id,
            binding=d["binding"],
            verdict=d["verdict"],
            time_obtained=d["time_obtained"],
            function_call=d["function_call"],
            collapsing_atom=d["collapsing_atom"]
        )

    else:

        raise Exception("Cannot instantiate single or multiple verdicts with parameters given.")

def list_verdicts_with_value(value):

    """called as list_verdicts(True) or list_verdicts(False)
    returns a list of objects 'class verdict' with the given value"""

    connection = get_connection()

    str=connection.request('client/list_verdicts_with_value/%d/' % value)
    if str=="None": raise ValueError('there are no such verdicts')
    verdicts_dict=json.loads(str)
    verdicts_list=[]
    for v in verdicts_dict:
        verdict_class=verdict(v["id"],v["binding"],v["time_obtained"],v["function_call"],v["collapsing_atom"])
        verdicts_list.append(verdict_class)
    return verdicts_list


def list_verdicts_dict_with_value(value):

    """finds all verdicts in the database with given value
    returns a dictionary with keys:
    from verdict - id, binding, verdict, time_obtained,
    from function_call - function, time_of_call
    from function - fully_qualified_name, property"""

    connection = get_connection()

    str=connection.request('client/list_verdicts_function_property_by_value/%d/' % value)
    if str=="None": raise ValueError('there are no such verdicts')
    d=json.loads(str)
    return d


class HTTPRequest(object):
    """
    class http_request represents the http_request table in the database
    initialized as http_request(id=1) or http_request(time_of_request=t)
    """

    def __init__(self, id=None, time_of_request=None):
        connection = get_connection()
        if id!=None:
            self.id=id
            if time_of_request==None:
                str=connection.request('client/get_http_by_id/%d/' % self.id)
                if str=="None": raise ValueError('no HTTP requests in the database with given ID')
                str=str[1:-1]
                d=json.loads(str)
                self.time_of_request=d["time_of_request"]
            else:
                self.time_of_request=time_of_request
        elif time_of_request!=None:
            self.time_of_request=time_of_request
            str=connection.request('client/get_http_by_time/%s/' % self.time_of_request)
            if str=="None": raise ValueError('no HTTP requests in the database with given time')
            str=str[1:-1]
            d=json.loads(str)
            self.id=d["id"]
        else:
            raise ValueError('either id or time_of_request argument required')

    def get_calls(self):
        connection = get_connection()
        str=connection.request('client/list_function_calls_http/%d/'% self.id)
        if str=="None":
            print('no calls during the given request')
            return
        calls_dict=json.loads(str)
        calls_list=[]
        for call in calls_dict:
            call_class=FunctionCall(call["id"],call["function"],call["time_of_call"], call["end_time_of_call"],call["http_request"])
            calls_list.append(call_class)
        return calls_list

def http_request(id=None, time_of_request=None):
    """
    Factory function for HTTP requests.
    """
    return HTTPRequest(id, time_of_request)


class Atom(object):
    """
    initialized as either atom(id=n) or atom(index_in_atoms=n)
    or with all arguments if known
    """

    def __init__(self,id=None,property_hash=None,serialised_structure=None,index_in_atoms=None):
        connection = get_connection()
        if id!=None and property_hash!=None and serialised_structure!=None and index_in_atoms!=None:
            self.id=id
            self.property_hash=property_hash
            self.serialised_structure=serialised_structure
            self.index_in_atoms=index_in_atoms
        else:
            if id!=None:
                self.id=id
                str=connection.request('client/get_atom_by_id/%d/' % self.id)
                if str=="None": raise ValueError('no atoms with given ID')
                str=str[1:-1]
                d=json.loads(str)
                self.property_hash=d["property_hash"]
                self.serialised_structure=d["serialised_structure"]
                self.index_in_atoms=d["index_in_atoms"]
            elif index_in_atoms!=None and property_hash!=None:
                self.index_in_atoms=index_in_atoms
                self.property_hash=property_hash
                str=connection.request('client/get_atom_by_index_and_property/%d/%s/' % (self.index_in_atoms,self.property_hash))
                if str=="None": raise ValueError('no such atoms')
                str=str[1:-1]
                d=json.loads(str)
                self.serialised_structure=d["serialised_structure"]
                self.id=d["id"]
            else:
                raise ValueError('either id or index_in_atoms and property arguments needed to initialize object')

    def __repr__(self):
        return "<%s id=%i, property_hash=%s, index_in_atoms=%i, structure=(%s)>" %\
            (
                self.__class__.__name__,
                self.id,
                self.property_hash,
                self.index_in_atoms,
                str(self.get_structure())
            )

    def get_structure(self):
        """
        atom.get_structure() returns the serialised structure of the atom in decoded format
        """
        str=self.serialised_structure
        obj=pickle.loads(str)
        return obj

def get_atom_list(verdict_value):
    """
    the idea is to list all atoms for which verdict is ture or false
    """

    connection = get_connection()

    str=connection.request(get_server()+'client/list_atoms_where_verdict/%d/'% verdict_value)
    if str=="None":
        raise ValueError('there are no verdicts with given value')
        return
    atoms_dict=json.loads(str)
    atoms_list=[]
    for atom_elem in atoms_dict:
        atom_class=atom(atom_elem["id"],atom_elem["property_hash"],atom_elem["serialised_structure"],atom_elem["index_in_atoms"])
        atoms_list.append(atom_class)
    return atoms_list

class instrumentation_point:

    def __init__(self,id,serialised_condition_sequence=None,reaching_path_length=None):
        connection = get_connection()
        self.id=id
        if serialised_condition_sequence==None or reaching_path_length==None:
            str=connection.request('client/get_instrumentation_point_by_id/%d/' % self.id)
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
        connection = get_connection()
        str=connection.request('client/list_observations_of_point/%d/'% self.id)
        if str=="None":
            print('no observations for given instrumentation point')
            return
        obs_dict=json.loads(str)
        obs_list=[]
        for o in obs_dict:
            obs_class=observation(o["id"],o["instrumentation_point"],o["verdict"],o["observed_value"],o["atom_index"],o["previous_condition"])
            obs_list.append(obs_class)
        return obs_list



class Observation(object):

    def __init__(self,id,instrumentation_point=None,verdict=None,observed_value=None,atom_index=None,previous_condition=None):
        self.id = id
        self.instrumentation_point = instrumentation_point
        self.verdict = verdict
        self.observed_value = observed_value
        self.atom_index = atom_index
        self.previous_condition = previous_condition

    def __repr__(self):
        return "<%s id=%i, instrumentation_point=%i, verdict=%i, observed_value=%s, atom_index=%i, previous_condition=%i>" %\
            (
                self.__class__.__name__,
                self.id,
                self.instrumentation_point,
                self.verdict,
                self.observed_value,
                self.atom_index,
                self.previous_condition
            )

    def get_assignments(self):
        connection = get_connection()
        str=connection.request('client/list_assignments_given_observation/%d/'% self.id)
        if str=="None": raise ValueError('no assignments paired with given observation')
        assignment_dict=json.loads(str)
        assignment_list=[]
        for a in assignment_dict:
            assignment_class=Assignment(a["id"])
            assignment_list.append(assignment_class)
        return assignment_list

    def get_assignments_as_dictionary(self):
        connection = get_connection()
        str=connection.request('/client/get_assignment_dict_from_observation/%d/'% self.id)
        if str=="None": raise ValueError('no assignments paired with given observation')
        assignment_dict=json.loads(str)
        for a in assignment_dict:
            # TODO: use assignment_dict[a][1] to decide if we need to import another type
            assignment_dict[a] = pickle.loads(assignment_dict[a][0])
        return assignment_dict

    def verdict_severity(self):
        """
        TODO: modify to support mixed atoms.
        """
        formula=verdict(self.verdict).get_collapsing_atom().get_structure()
        interval=formula._interval
        lower=interval[0]
        upper=interval[1]
        x=float(self.observed_value)
        #d is the distance from observed value to the nearest interval bound
        d=min(abs(x-lower),abs(x-upper))
        #sign=-1 if verdict value=0 and sign=1 if verdict is true
        sign=-1+2*(formula.check(x))
        return sign*d

    def get_instrumentation_point(self):
        return instrumentation_point(id=self.instrumentation_point)

def observation(id,instrumentation_point=None,verdict=None,observed_value=None,atom_index=None,previous_condition=None):
    """
    Factory function for observations.
    """
    connection = get_connection()
    if instrumentation_point==None or verdict==None or observed_value==None or atom_index==None or previous_condition==None:
        str=connection.request('client/get_observation_by_id/%d/' % self.id)
        if str=="None": raise ValueError('there is no observation with given id')
        str=str[1:-1]
        d=json.loads(str)

        return Observation(
            id = id,
            instrumentation_point=d["instrumentation_point"],
            verdict=d["verdict"],
            observed_value=d["observed_value"],
            atom_index=d["atom_index"],
            previous_condition=d["previous_condition"]
        )
    else:
        return Observation(
            id = id,
            instrumentation_point=instrumentation_point,
            verdict=verdict,
            observed_value=observed_value,
            atom_index=atom_index,
            previous_condition=previous_condition
        )

class Assignment(object):
    def __init__(self,id):
        connection = get_connection()
        self.id=id
        str=connection.request('client/get_assignment_by_id/%d/' % self.id)
        if str=="None": raise ValueError('there is no assignment with given id')
        str=str[1:-1]
        d=json.loads(str)
        self.variable=d["variable"]
        self.value=d["value"] #is it better to keep this serialised or to deserialise it?
        self.type=d["type"]
