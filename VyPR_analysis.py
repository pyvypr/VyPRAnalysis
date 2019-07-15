import json
import requests
import urllib2
from datetime import datetime
import pickle
#from VyPR import monitor_synthesis
#from flask import jsonify
import sys
sys.path.append("VyPR/")
from monitor_synthesis.formula_tree import *

#server_url is a global variable which can be changed by passing a string to the set_server() function
server_url=json.load(open('config.json'))["verdict_server_url"]
def set_server(given_url):
    global server_url
    server_url=given_url

#class function represents the table function in the database
#it is initialized by its name, but Function can be used to initialize the class by function id
class function:
    def __init__(self, fully_qualified_name):
        self.fully_qualified_name=fully_qualified_name
        str=urllib2.urlopen(server_url+'client/get_function_by_name/%s/' % fully_qualified_name).read()
        str=str[1:-1]
        f_dict=json.loads(str)
        self.id=f_dict["id"]
        self.property=f_dict["property"]
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
    #def get_graph(self):
        #returns scfg of function



def Function(function_id):
    str=urllib2.urlopen(server_url+'client/get_function_by_id/%d/' % function_id).read()
    str=str[1:-1]
    f_dict=json.loads(str)
    return function(f_dict["fully_qualified_name"])

class property:
 def __init__(self, hash, serialised_structure):
  self.hash=hash
  self.serialised_structure=serialised_structure

class binding:
  def __init__(self,id,binding_space_index,function,binding_statement_lines):
    self.id=id
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
    def first_observation_fail():
        #observation.verdict gives a verdict - we need all observations such that
        #verdict(observation.verdict).function_call=self.id 

        return observation()

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

#both classes http_request and HTTPRequest represent the same table in the database
#HTTPRequest is used to initialize the request object by time of request, while the other one
#initializes the object by id or if both values are known
#should this be replaced by one class initialized as http_request(id=1) or http_request(time_of_request=t)?
class http_request:
    def __init__(self, id, time_of_request=None):
        self.id=id
        if time_of_request==None:
            str=urllib2.urlopen(server_url+'client/get_http_by_id/%d/' % self.id).read()
            str=str[1:-1]
            d=json.loads(str)
            self.time_of_request=d["time_of_request"]
        else:
            self.time_of_request=time_of_request
    def get_calls(self):
        str=urllib2.urlopen(server_url+'client/list_function_calls_http/%d/'% self.id).read()
        calls_dict=json.loads(str)
        calls_list=[]
        for call in calls_dict:
            call_class=function_call(call["id"],call["function"],call["time_of_call"],call["http_request"])
            calls_list.append(call_class)
        return calls_list

class HTTPRequest:
    def __init__(self, time_of_request):
        self.time_of_request=time_of_request
        str=urllib2.urlopen(server_url+'client/get_http_by_time/%s/' % self.time_of_request).read()
        str=str[1:-1]
        d=json.loads(str)
        self.id=d["id"]

#atom.get_structure() returns the serialised structure of the atom in decoded format
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
            else:
                self.index_in_atoms=index_in_atoms
                str=urllib2.urlopen(server_url+'client/get_atom_by_index/%d/' % self.index_in_atoms).read()
                str=str[1:-1]
                d=json.loads(str)
                self.property_hash=d["property_hash"]
                self.serialised_structure=d["serialised_structure"]
                self.id=d["id"]
    def get_structure(self):
        str=self.serialised_structure
        obj=pickle.loads(str)
        return obj

#the idea is to list all atoms for which verdict is ture or false, is it even useful?
def get_atom_list(verdict_value):
    str=urllib2.urlopen(server_url+'client/list_atoms_where_verdict/%d/'% verdict_value).read()
    atoms_dict=json.loads(str)
    atoms_list=[]
    for atom_elem in atoms_dict:
        atom_class=atom(atom_elem["id"],atom_elem["property_hash"],atom_elem["serialised_structure"],atom_elem["index_in_atoms"])
        atoms_list.append(atom_class)
    return atoms_list

"""
class atom_instrumentation_point_pair:
    def __init__(self,id):

class binding_instrumentation_point_pair:
    def __init__(self,id):


class instrumentation_point:
    def __init__(self,id):
"""

class observation:
    def __init__(self,id):
        self.id=id
        str=urllib2.urlopen(server_url+'client/get_observation_by_id/%d/' % self.id).read()
        str=str[1:-1]
        d=json.loads(str)
        self.instrumentation_point=d["instrumentation_point"]
        self.verdict=d["verdict"]
        self.observed_value=d["observed_value"]
        self.atom_index=d["atom_index"]
        self.previous_condition=d["previous_condition"]

"""
class observation_assignment_pair:
    def __init__(self,id):


class assignment:
    def __init__(self,id):


class path_condition_structure:
    def __init__(self,id):


class path_condition:
    def __init__(self,id):
"""

#def write_scfg(scfg_object,file_name):


def main():
    """f1=function('app.routes.paths_branching_test')
    f2=Function(1)
    function_calls1=f1.get_calls()
    function_calls2=f2.get_calls()
    print(len(function_calls1))
    print(len(function_calls1))

    req=http_request(1)
    print(req.time_of_request)
    req1=HTTPRequest(req.time_of_request)
    print(req1.id)

    function_calls3=f2.get_calls(req1)
    print(function_calls3[0].http_request)"""
    set_server("http://127.0.0.1:9005/")
    verdict1=verdict(1)
    atom1s=verdict1.get_atom().get_structure()
    print(atom1s)

    print(len(get_atom_list(0)))

if __name__ == "__main__":
    main()
