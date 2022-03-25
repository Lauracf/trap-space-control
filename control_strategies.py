from itertools import combinations, product

from pyboolnet.trap_spaces import compute_trap_spaces, compute_trapspaces_that_intersect_subspace


def run_control_problem(primes, target, intervention_type, control_type, avoid_nodes: dict = {}, avoid_edges: dict = {}, limit: int = 3, output_file: str = "", use_attractors: bool = True, complex_attractors: List[List[dict]] = []):

    # Setting targets and computing selected trap spaces

    if control_type in ["trap_spaces", "transient", "both"]:
        tspaces = compute_trapspaces_that_intersect_subspace(primes=primes, subspace=target, type_="percolated", max_output=1000000)
        if {} not in tspaces:
            tspaces.append({})
        tsmin = compute_trap_spaces(primes, "min")
        target_trap_spaces = select_trapspaces(tspaces=tspaces, subspace=target, use_attractors=use_attractors, tsmin=tsmin, complex_attractors=complex_attractors)
        target_percolation = []
        print("Num of selected trap spaces:", len(target_trap_spaces))

        if control_type == "transient":
            target_percolation = target_trap_spaces
            target_trap_spaces = []

        elif control_type == "both":
            target_percolation = [target]
    else:
        target_trap_spaces = []
        target_percolation = [target]

    # Computing CS in ASP

    create_asp_program_instance(primes=primes, intervention_type=intervention_type, target_trap_spaces=target_trap_spaces, target_subspaces=target_percolation, max_size=limit, avoid_nodes=avoid_nodes, avoid_edges=avoid_edges, filename="program_instance")
    system("rm output_asp.txt")
    command_ts = "clingo --enum-mode=domRec --heuristic=Domain --dom-mod=5,16 " + "program_instance.asp control_node_and_edge.asp 0 >> output_asp.txt"
    system(command_ts)
    cs_asp = read_intv_from_asp_output(primes=primes, filename="output_asp.txt", node_intervention="node")
    print("Number of CS asp:", results_info(cs_asp))

    # Saving output

    if output_file != "":
        with open(output_file+".py", "w") as f:
            f.write("Target = " + pformat(target) + "\n")
            f.write("#Control strategies using " + control_type + "\ncs = " + pformat(cs_asp) + "\n")

    return cs_asp


def create_asp_program_instance(primes: dict, intervention_type: str, target_trap_spaces: List[dict] = [], target_subspaces: List[dict] = [], max_size: int = 3, avoid_nodes: List[str] = [], avoid_edges: List[str] = [], filename: str = "") -> str:
    """
    Encodes the control strategy problem is ASP.
    The output is a string. If *filename* is provided, it saves the output on a file.
    """

    # Encoding of the Boolean function
    nodes_to_avoid = ""
    edges_to_avoid = ""
    for x in avoid_edges:
        edges_to_avoid = edges_to_avoid + "avoid_edge(" + x[0] + "," + x[1] + "). "
    formulas = ""
    dnfs = ""
    clauses = ""
    clauses_dict = dict()
    primes_included = dict()
    id_form = -1
    cont_clause = 0
    for x in primes.keys():
        id_form = id_form + 1
        if x in avoid_nodes:
            nodes_to_avoid = nodes_to_avoid + "avoid_node(" + x + "). "
        formulas = formulas + "formula(" + x + ", " + str(id_form) + "). "
        for p in primes[x][1]:
            id_clause = str(cont_clause)
            cont_clause = cont_clause + 1
            text_clause = ""
            for y in p.keys():
                value = str(p[y])
                if str(p[y]) == "0":
                    value = "-1"
                text_clause = text_clause + "clause(" + id_clause + ", " + y + ", " + value + "). "
            clauses_dict[id_clause] = text_clause
            clauses = clauses + text_clause
            dnfs = dnfs + "dnf(" + str(id_form) + ", " + id_clause + "). "
    # Encoding goal subspaces
    subspaces = ""
    goals = ""

    id_subspace = 0
    for s in target_subspaces:
        id_subspace = id_subspace - 1
        subspaces = subspaces + "subspace(" + str(id_subspace) + "). "
        for x in s.keys():
            value = str(s[x])
            if str(s[x]) == "0":
                value = "-1"
            goals = goals + "goal(" + str(id_subspace) + ", " + x + ", " + value + "). "

    id_subspace = -1
    for s in target_trap_spaces:
        id_subspace = id_subspace + 1
        subspaces = subspaces + "subspace(" + str(id_subspace) + "). "
        for x in s.keys():
            value = str(s[x])
            if str(s[x]) == "0":
                value = "-1"
            goals = goals + "goal(" + str(id_subspace) + ", " + x + ", " + value + "). "

    max_nodes = max_size
    max_edges = max_size
    if intervention_type == "node":
        max_edges = -1
    if intervention_type == "edge":
        max_nodes = -1
    constants = "#const maxsize=" + str(max_size) + "." + "\n\n" + "#const maxnodes=" + str(max_nodes) + "." + "\n\n" + "#const maxedges=" + str(max_edges) + "."

    final_text = nodes_to_avoid + "\n\n" + edges_to_avoid + "\n\n" + formulas + "\n\n" + dnfs + "\n\n" + clauses + "\n\n" + subspaces + "\n\n" + goals + "\n\n" + constants
    if filename != "":
        # Saving file
        with open(filename + ".asp", "w") as file:
            file.write(final_text.lower())
    return final_text


def read_intv_from_asp_output(primes: dict, filename: str):
    cs_total = list()
    file = open(filename)
    text = file.read()
    text = text.split("\n")
    if any(lin == "UNSATISFIABLE" for lin in text):
        return([])
    else:
        for lin in text:
            if "node" in lin or "edge" in lin:
                cs = dict()
                parts = lin.split(" ")
                for x in parts:
                    if "edge" in x:
                        y = x.replace("edge", "").replace("(", "").replace(")", "").split(",")
                        y[2] = int(y[2])
                        if y[2] == -1:
                            y[2] = 0
                        for n in primes.keys():
                            if n.lower() == y[0]:
                                y[0] = n
                            if n.lower() == y[1]:
                                y[1] = n
                        cs[(y[0], y[1])] = y[2]
                    if "node" in x:
                        y = x.replace("node", "").replace("(", "").replace(")", "").split(",")
                        y[1] = int(y[1])
                        if y[1] == -1:
                            y[1] = 0
                        for n in primes.keys():
                            if n.lower() == y[0]:
                                y[0] = n
                        cs[y[0]] = y[1]
                cs_total.append(cs)
        if len(cs_total) == 0:
            cs_total.append({})
    return(cs_total)


def is_included_in_subspace(subspace1: dict, subspace2: dict):
    """
    Test whether *subspace1* is contained in *subspace2*.

    **arguments**:
        * *subspace1*, *subspace2* (dicts): subspaces.
    **returns**:
        * Answer (bool): whether *subspace1* is contained in *subspace2*.
    **example**::
        >>> is_included_in_subspace({'v1': 0, 'v2': 1}, {'v2': 1})
        True
    """

    return all(x in subspace1 and subspace1[x] == subspace2[x] for x in subspace2.keys())


def select_trapspaces(tspaces, subspace: dict, use_attractors: bool = False, tsmin: List[dict] = None, complex_attractors: List[dict] = None):
    """
    Returns the trap spaces from *tspaces* that are contained in *subspace*.
    If *use_attractors* is True, it also returns the trap spaces from *tspaces* that contain only elements from *tsmin* and *complex_attractors* that are contained in *subspace*.
    It does not check that the elements of *tsmin* are minimal trap spaces or that the elements of *complex_attractors* are attractors.
    **arguments**:
        * *tspaces*: list of trap spaces.
        * *subspace*: subspace.
        * *use_attractors* (bool): indicates whether attractors are used in the selection of trap spaces or not. Default value: False.
        * *tsmin*: minimal trap spaces. Only used when *use_attractors* is True. Default value: [].
        * *complex_attractors*: list of complex attractors. A complex attractor is expected as a list of states (dicts). Only used when *use_attractors* is True. Default value: [].
    **returns**:
        * Selected (list): the trap spaces contained in *subspace* and, if *use_attractors* is True, also the trap spaces that contain only elements from *Tsmin* and *ComplexAttractors* that are contained in *subspace*.
    **example**::
        >>> selectTrapSpaces([{'v1': 0,'v2': 1}, {'v1': 0,'v3': 1}, {'v1': 0,'v2': 1,'v3': 1}], {'v2': 1})
        [{'v1': 0,'v2': 1}, {'v1': 0,'v2': 1,'v3': 1}]
    """

    if not tsmin:
        tsmin = []
    if not complex_attractors:
        complex_attractors = []

    # Trap spaces contained in *subspace*
    sel1 = [x for x in tspaces if is_included_in_subspace(x, subspace)]

    if not use_attractors:
        return sel1

    # Classify minimal trap spaces and complex attractors
    tsmin_accepted = [x for x in tsmin if is_included_in_subspace(x, subspace)]
    tsmin_discarded = [x for x in tsmin if x not in tsmin_accepted]
    cattr_accepted = [x for x in complex_attractors if all(is_included_in_subspace(y, subspace) for y in x)]
    cattr_discarded = [x for x in complex_attractors if x not in cattr_accepted]

    # If conditions cannot be matched
    if len(tsmin_accepted) + len(cattr_accepted) == 0:
        return sel1

    # If all trap spaces satisfy the condition
    if len(tsmin_discarded) + len(cattr_discarded) == 0:
        return tspaces

    tspaces_left = [x for x in tspaces if x not in sel1]
    sel2 = [ts for ts in tspaces_left
            if (any(is_included_in_subspace(x, ts) for x in tsmin_accepted) or
                any(is_included_in_subspace(y, ts) for x in cattr_accepted for y in x))
               and not any(is_included_in_subspace(y, ts) for y in tsmin_discarded)
               and not any(is_included_in_subspace(y, ts) for x in cattr_discarded for y in x)]

    return sel1 + sel2


def results_info(list_cs: List[dict]):
    """
    Returns a string stating the amount and size of the elements in *list_cs*.
    **returns**:
        * *text* (string): text stating the number and size of the elements in *CS*.
    **example**::
        >>> results_info([{'v1': 1}, {'v2':0, 'v3':1}])
    "2 control strategies, 1 of size 1, 1 of size 2"
    """

    text = str(len(list_cs)) + " control strategies"
    sizes = [len(x) for x in list_cs]
    cs_sizes = list({(el, sizes.count(el)) for el in sizes})
    cs_sizes.sort()
    for x in cs_sizes:
        text = text + ", " + str(x[1]) + " of size " + str(x[0])
    return text
