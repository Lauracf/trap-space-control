# Control strategies via trap spaces

This repository contains the source code for the method to identify control strategies for Boolean networks using Answer Set Programming, as described in the paper titled "Node and edge control strategy identification via trap spaces in Boolean networks". A preprint version is available at

 * TBA


The paper above is an extended version of the paper "Control Strategy Identification via Trap Spaces in Boolean Networks" accepted at Computational Methods in Systems Biology (CMSB) 2020, available at

 * https://doi.org/10.1007/978-3-030-60327-4_9


## Requirements

The code requires the use of PyBoolNet, a python package for the generation, modification and analysis of Boolean networks. Information about PyBoolNet, user manual and installation can be found at

* https://github.com/hklarner/PyBoolNet

The code works with Boolean networks in BoolNet format.


## Description

The main functions are included in *control_strategies.py*. The files *case_study_mapk.py* or *case_study_tlgl.py* show examples of how to use *control_strategies.py*, setting the parameters for the control strategy identification.

### Setting the parameters

 * **bnet** (string): file of the Boolean network in BoolNet format.
 * **target** (dictionary): subspace defining the target.
 * **intervention_type** (string): type of interventions. The options are *node*, *edge* or *combined*.
 * **control_type** (string): type of control. The options are *percolation*, *trap_spaces* or *both*.
 * **update** (string): type of update. The options are *asynchronous*, *synchronous* or *mixed*.
 * **avoid_nodes** (list): nodes that cannot be part of the control strategies.
 * **avoid_edges** (list): edges that cannot be part of the control strategies.
 * **limit** (integer): upper limit on the size of the control strategies.
 * **use_attractors** (bool): indicates whether the trap spaces can be selected using the information about the attractors.
 * **complex_attractors** (list): if needed, complex attractors that are not minimal trap spaces.
 * **output_file** (string): file where the results are stored.
 
 
Note that subspaces are represented using Python dictionaries, where the fixed variables and their values are the keys and the values, respectively, of the dictionary. A complex attractor is expected as the list of the states that belong to it, each state expressed as a subspace.

