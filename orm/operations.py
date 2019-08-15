"""
Module that contains functions to perform operations with ORM classes.
"""

import requests
import json
from pprint import pprint
import urllib2

# VyPR imports
import VyPR.control_flow_graph.construction

# VyPRAnalysis imports
from VyPRAnalysis import get_server
from VyPRAnalysis.orm.base_classes import function, observation, instrumentation_point
from VyPRAnalysis.path_reconstruction import edges_from_condition_sequence, deserialise_condition

def get_parametric_path(obs_id_list,instrumentation_point_id):
    #instrumentation_point optional -> get it from an observation in the list??
    for id in obs_id_list:
        obs=observation(id)
        if obs.instrumentation_point!=instrumentation_point_id:
            raise ValueError('the observations must have the same instrumentation point')

    data1={"observation_ids":obs_id_list, "instrumentation_point_id":instrumentation_point_id}
    req=requests.post(url=get_server()+'get_parametric_path/',data=json.dumps(data1))

    return req.text


def get_intersection_from_observations(function_name,obs_id_list,inst_point):

    f=function(fully_qualified_name=function_name)
    subchain_text=get_parametric_path(obs_id_list,inst_point)
#    print(subchain_text)
    subchain_dict=json.loads(subchain_text)
#    pprint(subchain_dict)

    paths=[]
    seq=subchain_dict["intersection_condition_sequence"]
    scfg=f.get_graph()
    ipoint=instrumentation_point(inst_point)

    intersection_path=edges_from_condition_sequence(
        scfg,
        map(deserialise_condition, seq[1:]),
        ipoint.reaching_path_length
    )
#    print("intersection with condition sequence \n%s\n path length %i is\n %s" % (str(seq[1:]), ipoint.reaching_path_length, str(intersection_path)))
#    edit_code(intersection_path)
#    print("------------------------------------------------")
#    print(seq)
    return intersection_path


def get_paths_from_observations(function_name,obs_id_list,inst_point):
    """
    returns a list of paths taken before each of the given observations
    """

    f=function(fully_qualified_name=function_name)
    subchain_text=get_parametric_path(obs_id_list,inst_point)
    subchain_dict=json.loads(subchain_text)
    #pprint(subchain_dict)

    paths=[]
    seq=subchain_dict["intersection_condition_sequence"]

    for id in obs_id_list:

        subchain=[]
        ind=0

        while ind<len(seq):
            if seq[ind]=="parameter":
                cond=((subchain_dict["parameter_maps"])["0"])[str(obs_id_list.index(id))]
                for cond_elem in cond:
#                    print(cond_elem)
                    subchain.append(deserialise_condition(cond_elem))
            else:
                subchain.append(seq[ind])
            ind+=1

        subchain = subchain[1:]
        scfg=f.get_graph()
        ipoint=instrumentation_point(inst_point)
        path=edges_from_condition_sequence(scfg,subchain,ipoint.reaching_path_length)
        paths.append(path)

    return paths


def edit_code(path):
    condition_lines=set()
    #doing this as a set to avoid highlighting the same lines multiple times
    for path_elem in path:
        if type(path_elem) is VyPR.control_flow_graph.construction.CFGVertex:
            condition_lines.add(path_elem._structure_obj.lineno)

#    print("condition lines", condition_lines)

    file=open("routes.py.inst","r")
    lines=file.readlines()
    for line_ind in condition_lines:
        lines[line_ind-1]='*'+lines[line_ind-1]

    for line in lines:
        print(line.rstrip())
    file=open("changed_routes.py.inst","w")
    file.writelines(lines)
    file.close()

def list_observations():
    str=urllib2.urlopen(get_server()+'client/list_observations/').read()
    if str=="None":
        raise ValueError('no observations')
        return
    obs_dict=json.loads(str)
    obs_list=[]
    for o in obs_dict:
        obs_class=observation(o["id"],o["instrumentation_point"],o["verdict"],o["observed_value"],o["atom_index"],o["previous_condition"])
        obs_list.append(obs_class)
    return obs_list

def list_functions():
    str=urllib2.urlopen(get_server()+'client/list_functions/').read()
    if str=="None":
        raise ValueError('no functions')
        return
    f_dict=json.loads(str)
    f_list=[]
    for f in f_dict:
        f_class=function(f["id"],f["fully_qualified_name"],f["property"])
        f_list.append(f_class)
    return f_list
