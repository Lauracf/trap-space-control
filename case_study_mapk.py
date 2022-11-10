from control_strategies import *
from pprint import pformat

from pyboolnet.file_exchange import bnet2primes

if __name__ == "__main__":

    # Reading network

    bnet = "Networks/grieco_mapk.bnet"
    primes = bnet2primes(bnet)

    # Setting parameters

    intervention_type = "node"  # Options: "node", "edge", "combined"
    control_type = "both"  # Options: "percolation", "trap_spaces", "both"
    update = "asynchronous"
    target = {"Apoptosis": 1, "Proliferation": 0, "Growth_Arrest": 1}
    avoid_nodes = []
    avoid_edges = []
    limit = 3

    use_attractors = True
    complex_attractors = []
    output_file = ""

    # Computing control strategies
    print("Network:", bnet, "- Type:", intervention_type, "-", control_type)

    cs = run_control_problem(
        primes=primes,
        target=target,
        intervention_type=intervention_type,
        control_type=control_type,
        avoid_nodes=avoid_nodes,
        avoid_edges=avoid_edges,
        limit=limit,
        output_file=output_file,
        use_attractors=use_attractors,
        complex_attractors=complex_attractors)

    print(results_info(cs))
