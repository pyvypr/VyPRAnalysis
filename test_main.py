import VyPR_analysis as analysis
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import pickle
import argparse

def plot_severity_vs_time(f,severity_function=analysis.verdict_severity):
    #get a function call of the given function such that there was a failure during the call
    call=f.get_calls_with_verdict(0)[0]

    #find the first observation wrt verdicts that caused the failure
    failed_observation=call.get_falsifying_observation()

    #find the instrumentation point at which the failed observation failed
    inst_point=failed_observation.get_instrumentation_point()

    #get all the observations of that instrumentation point, whether they failed or not
    observations=inst_point.get_observations()
    ids=[] #will contain IDs of assignments
    t=[]
    s=[]

    #grouping observations by the assignments they are paired with
    #t and s are lists, they have as many elements as there are groups (assignments)
    #their elements are lists of time points and verdict severity values
    valuations=[]
    for obs in observations:
        assignments=obs.get_assignments()
        print(obs.id)
        final_dict=dict()
        for a in assignments:
            a=vars(a)
            a["value"]=pickle.loads(a["value"])
            print(a)
            final_dict[a["variable"]]=a["value"]

        if final_dict not in valuations:
            valuations.append(final_dict)
            t.append([])
            s.append([])

        time=analysis.verdict(obs.verdict).time_obtained
        t[valuations.index(final_dict)].append(datetime.strptime(time,'%Y-%m-%dT%H:%M:%S.%f'))
        s[valuations.index(final_dict)].append(severity_function(obs))

    """
    #this part is for plotting multiple figures into the same file
    fig, ax = plt.subplots(nrows=1,ncols=len(ids))
    for i in ids:
        ind=ids.index(i)
        ax[ind].plot(t[ind] ,s[ind],'.')
    """

    for v in valuations:
        ind=valuations.index(v)
        plt.plot(t[ind],s[ind],'ob')
        plt.xlabel('time verdict was obtained')
        plt.ylabel('verdict severity')
        plt.margins(0.05)
        plt.savefig('plot_%d.pdf'%ind)
        plt.close() #move after loop to get a plot of all dots on the same graph (coloured by assignment)

def main():
    parse = argparse.ArgumentParser(description="Testing script for VyPRAnalysis.")
    parse.add_argument('--port', type=int, help='The port number on which to connect to the verdict server.')
    parse.add_argument('--service-dir', type=str, help='The absolute directory in which to find the monitored service locally.')
    args = parse.parse_args()
    analysis.set_server("http://127.0.0.1:%i/" % args.port)
    f1=analysis.function(fully_qualified_name='app.routes.paths_branching_test')
    f2=analysis.function(id=1)
    function_calls1=f1.get_calls()
    function_calls2=f2.get_calls(1)
    print(len(function_calls1))
    print(len(function_calls2))

    req=analysis.http_request(id=1)
    print(req.time_of_request)
    req1=analysis.http_request(time_of_request=req.time_of_request)
    print(req1.id)

    function_calls3=f2.get_calls(req1.id)
    print(function_calls3[0].http_request)

    verdict1=analysis.verdict(1)
    atom1s=verdict1.get_collapsing_atom().get_structure()
    print(atom1s)

    obs=analysis.observation(id=1)
    print(obs.verdict_severity())

    true_verdicts=analysis.list_verdicts_dict_with_value(1)
    print(true_verdicts)
    for v in true_verdicts:
        print(v)
        print("function id=",v["function"])
        print("verdict time:",v["time_obtained"])

    print(len(analysis.get_atom_list(1)))
    call1=analysis.function_call(1)
    obs_fail=call1.get_falsifying_observation()
    if obs_fail!=None:
        print(obs_fail.id)

    pp=analysis.instrumentation_point(id=1)
    print(pp.serialised_condition_sequence)
    #ppp=analysis.assignment(id=1)
    #print(ppp.variable)
    graphfile=open("graph_file","w+")
    analysis.write_scfg(f1.get_graph(),"graph_file")
    graphfile.close()

    plot_severity_vs_time(analysis.function(1))

if __name__ == "__main__":
    main()
