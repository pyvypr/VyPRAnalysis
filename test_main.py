import VyPR_analysis as analysis

def main():
    analysis.set_server("http://127.0.0.1:9005/")
    f1=analysis.function(fully_qualified_name='app.routes.paths_branching_test')
    f2=analysis.function(id=1)
    function_calls1=f1.get_calls()
    function_calls2=f2.get_calls()
    print(len(function_calls1))
    print(len(function_calls2))

    req=analysis.http_request(id=1)
    print(req.time_of_request)
    req1=analysis.http_request(time_of_request=req.time_of_request)
    print(req1.id)

    function_calls3=f2.get_calls(req1)
    print(function_calls3[0].http_request)

    verdict1=analysis.verdict(1)
    atom1s=verdict1.get_atom().get_structure()
    print(atom1s)

    print(len(analysis.get_atom_list(1)))
    call1=analysis.function_call(1)
    obs_fail=call1.first_observation_fail()
    if obs_fail!=None:
        print(obs_fail.id)

    pp=analysis.instrumentation_point(id=1)
    print(pp.serialised_condition_sequence)
    #ppp=analysis.assignment(id=1)
    #print(ppp.variable)
    graphfile=open("graph_file","w+")
    analysis.write_scfg(f1.get_graph(),"graph_file")
    graphfile.close()

if __name__ == "__main__":
    main()
