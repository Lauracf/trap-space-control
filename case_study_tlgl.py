from control_strategies import *
from pprint import pformat

if __name__ == "__main__":

    # Reading network

    bnet = "Networks/zhang_tlgl.bnet"
    primes = PyBoolNet.FileExchange.bnet2primes(bnet)

    # Setting parameters

    intervention_type = "combined"  # Options: "node", "edge", "combined"
    control_type = "both"  # Options: "percolation", "trap_spaces", "both"
    update = "asynchronous"
    target = {"Apoptosis": 1, "Proliferation": 0}
    avoid_nodes = []
    avoid_edges = []
    limit = 3

    use_attractors = True
    complex_attractors = []
    output_file = ""

    # Computing control strategies
    print("Network:", network, "- Type:", intervention_type, "-", control_type)

    cs = run_control_problem(
        primes=primes,
        target=target,
        intervention_type=intervention_type,
        control_type=control_type,
        avoid_nodes=avoid_nodes,
        avoid_edges=avoid_edges,
        output_file=output_file,
        use_attractors=use_attractors,
        complex_attractors=complex_attractors)

    print(results_info)
