# Control strategies via trap spaces

This repository contains functions to identify control strategies for Boolean networks, as described in the paper titled "Control Strategy Identification via Trap Spaces in Boolean Networks" accepted at Computational Methods in Systems Biology (CMSB) 2020. A preprint version is available at

 * https://arxiv.org/abs/2005.09390


## Requirements

The code requires the use of PyBoolNet, a python package for the generation, modification and analysis of Boolean networks. Information about PyBoolNet, user manual and installation can be found at

* https://github.com/hklarner/PyBoolNet

The code works with Boolean networks in BoolNet format.


## Description

The main functions are included in *Control.py*. The files *control_strategies_mapk.py* or *control_strategies_tlgl.py* show examples of how to use *Control.py*, setting the parameters for the control strategy identification.

### Setting the parameters

 * **bnet_file** (string): file of the Boolean network in BoolNet format.
 * **type_CS** (string): type of control strategies that are computed. The options are *via_trapspaces*, *percolation_only* or *both*.
 * **phenotype** (dictionary): subspace defining the target phenotype.
 * **avoid_nodes** (list): nodes that cannot be part of the control strategies.
 * **limit** (integer): upper limit on the size of the control strategies.
 * **use_attractors** (bool): indicates whether the trap spaces can be selected using the information about the attractors.
 * **complex_attractors** (list): if needed, complex attractors that are not minimal trap spaces.
 * **comments** (bool): if active, information about the process and the control strategies computed is shown.
 * **output_file** (string): file where the results are stored.
 
 
Subspaces are represented with Python dictionaries, where the fixed variables and their values are the keys and the values, respectively, of the dictionary. A complex attractor is expected as the list of the states that belong to it, each state expressed as a subspace.

