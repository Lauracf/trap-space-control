import PyBoolNet
import itertools

def is_included_in_subspace(Subspace1, Subspace2):
	"""
	Tests whether *Subspace1* is contained in *Subspace2*.
	**arguments**:
		* *Subspace1*, *Subspace2* (dicts): subspaces.
	**returns**:
		* Answer (bool): whether *Subspace1* is contained in *Subspace2*.
	**example**::
		>>> is_included_in_subspace({'v1': 0, 'v2': 1}, {'v2': 1})
		True
	"""

	return all(x in Subspace1 and Subspace1[x]==Subspace2[x] for x in Subspace2.keys())


def select_trapspaces(Tspaces, Subspace, UseAttractors=False, Tsmin=None, ComplexAttractors=None):
	"""
	Returns the trap spaces from *Tspaces* that are contained in *Subspace*.
	If *UseAttractors* is True, it also returns the trap spaces from *Tspaces* that contain only elements from *Tsmin* and *ComplexAttractors* that are contained in *Subspace*.
	It does not check that the elements of *Tsmin* are minimal trap spaces or that the elements of *ComplexAttractors* are attractors.
	**arguments**:
		* *Tspaces*: list of trap spaces.
		* *Subspace*: subspace.
		* *UseAttractors* (bool): indicates whether attractors are used in the selection of trap spaces or not. Default value: False.
		* *Tsmin*: minimal trap spaces. Only used when *UseAttractors* is True. Default value: [].
		* *ComplexAttractors*: list of complex attractors. A complex attractor is expected as a list of states (dicts). Only used when *UseAttractors* is True. Default value: []. 
	**returns**:
		* Selected (list): the trap spaces contained in *Subspace* and, if *UseAttractors* is True, also the trap spaces that contain only elements from *Tsmin* and *ComplexAttractors* that are contained in *Subspace*.

	**example**::
		>>> selectTrapSpaces([{'v1': 0,'v2': 1}, {'v1': 0,'v3': 1}, {'v1': 0,'v2': 1,'v3': 1}], {'v2': 1})
		[{'v1': 0,'v2': 1}, {'v1': 0,'v2': 1,'v3': 1}]
	"""

	if not Tsmin: 
		Tsmin = []
	if not ComplexAttractors:
		ComplexAttractors = []

	# Trap spaces contained in *Subspace*
	sel1 = [x for x in Tspaces if is_included_in_subspace(x, Subspace)]

	if not UseAttractors:
		return sel1

	# Classify minimal trap spaces and complex attractors
	tsmin_accepted = [x for x in Tsmin if is_included_in_subspace(x,Subspace)]
	tsmin_discarded = [x for x in Tsmin if not x in tsmin_accepted]
	cattr_accepted = [x for x in ComplexAttractors if all(is_included_in_subspace(y,Subspace) for y in x)]
	cattr_discarded = [x for x in ComplexAttractors if not x in cattr_accepted]

	# If conditions cannot be matched
	if len(tsmin_accepted) + len(cattr_accepted) == 0:
		return sel1

	# If all trap spaces satisfy the condition
	if len(tsmin_discarded) + len(cattr_discarded) == 0:
		return Tspaces

	tspaces_left = [x for x in Tspaces if x not in sel1]
	sel2 = [ts for ts in tspaces_left
		    if (any(is_included_in_subspace(x, ts) for x in tsmin_accepted) or 
			    any(is_included_in_subspace(y, ts) for x in cattr_accepted for y in x))
		       and not any(is_included_in_subspace(y, ts) for y in tsmin_discarded) 
		       and not any(is_included_in_subspace(y, ts) for x in cattr_discarded for y in x)]

	return sel1 + sel2


def active_primes2(Primes, Subspace):
	"""
	Adapted from *PyBoolNet.PrimeImplicants.active_primes(Primes, Subspace)*
	Returns all primes from *Primes* that are active, i.e., consistent with *Subspace*.
	**arguments**:
		* *Primes*: prime implicants.
		* *Subspace* (dict): subspace.
	**returns**:
		* *active_primes* : primes from *Primes* that are consistent with *Subspace*.
	**example**::
		>>> active_primes2(primes, {'v1': 0,'v2': 1})
	"""

	active_primes = dict((name,[[],[]]) for name in Primes)
	for name in Primes:
		for v in [0,1]:
			for p in Primes[name][v]:
				if name in Subspace.keys():
					if Subspace[name]==v:
						if PyBoolNet.Utility.Misc.dicts_are_consistent(p,Subspace):
							active_primes[name][v].append(dict(p))
				else:
					if PyBoolNet.Utility.Misc.dicts_are_consistent(p,Subspace):
						active_primes[name][v].append(dict(p))
	return active_primes


def trapspaces_intersecting_subspace(Primes, Subspace, Type, MaxOutput=1000000, FnameASP=None, Representation="dict"):
	"""
	Adapted from *PyBoolNet.AspSolver.trapspaces_that_contain_state(Primes, State, Type, FnameASP=None, Representation="dict")*
	Computes trap spaces that have non-empty intersection with *Subspace*.
	It only returns the trivial trap space {} when no other trap spaces satisfying the conditions are found.
	**arguments**:
		* *Primes*: prime implicants.
		* *Suspace* (dict): subspace.
		* *Type* (str): either "min", "max", "all" or "percolated".
		* *MaxOutput*: maximum number of trap spaces calculated. Default value: 1000000.
		* *FnameASP* (str): file name or *None*. Default value: None.
		* *Representation* (str): either "str" or "dict", the representation of the trap spaces. Default value: "dict".
	**returns**:
		* *TrapSpaces* (list): the trap spaces that have non-empty intersection with *Subspace*.
	**example**::
		>>> trapspaces_intersecting_subspace(primes, {'v1': 1,'v2': 0,'v3': 0})
	"""

	assert(len(Primes) >= len(Subspace))
	assert(type(Subspace) in [dict])
	if type(Subspace)==str:
		Subspace = PyBoolNet.StateTransitionGraphs.state2dict(Primes,Subspace)
	active_primes = active_primes2(Primes, Subspace)
	# note: Bounds=(1,"n") enforces at least one variable fixed.
	#	   This is required for the subset maximal enumeration mode "--enum-mode=domRec --heuristic=Domain --dom-mod=3,16"
	#	   Otherwise clasp returns "*** Warn : (clasp): domRec ignored: no domain atoms found!"
	#	   Consequence: The trivial subspace is equivalent to the ASP problem being UNSATISFIABLE
	tspaces = PyBoolNet.AspSolver.potassco_handle(active_primes, Type=Type, Bounds=(1,"n"), Project=[], MaxOutput=MaxOutput, FnameASP=FnameASP, Representation=Representation)
	if not tspaces:
		# ASP program is unsatisfiable
		answer = {}
		if Representation=="str":
			answer = PyBoolNet.StateTransitionGraphs.subspace2str(Primes, answer)
		return [answer]
	return tspaces

def control_strategies_percolation_only(Primes, Subspace, Limit=3, Silent=False, StartingLength=0, PreviousCS=None, AvoidNodes=None):
	"""
	Computes control strategies for *Subspace* using only percolation.
	It does not check that the elements of *PreviousCS* are control strategies.

	**arguments**:
		* *Primes*: prime implicants.
		* *Suspace* (dict): subspace.
		* *Limit* (int): maximal size of the control strategies. Default value: 3.
		* *Silent* (bool): not print infos to screen. Default value: False.
		* *StartingLength* (int): minimal size of the control strategies. Default value: 0.
		* *PreviousCS* (list): list of already identified control strategies. Default value: empty list.
		* *AvoidNodes* (list): list of nodes that cannot be part of the control strategies. Default value: empty list.
	**returns**:
		* *CS* (list): list of control strategies (dict) of *Subspace* obtained by percolation.
	**example**::
		>>> controlStrategies_percolation_only(primes, {'v1': 1})
	"""

	if not PreviousCS: 
		PreviousCS = []
	if not AvoidNodes:
		AvoidNodes = []

	# Identifying control strategies
	candidates = [x for x in Primes.keys() if not x in AvoidNodes]
	CS = PreviousCS
	for i in range(StartingLength, Limit+1):
		if not Silent: print("Checking control strategies of size",i)
		for vs in itertools.combinations(candidates,i):
			subsets = itertools.product(*[(0,1)]*i)
			for ss in subsets:
				S = dict(zip(vs,ss))
				if not any(is_included_in_subspace(S,x) for x in CS):
					perc = PyBoolNet.AspSolver.percolate_trapspace(Primes,S)
					if is_included_in_subspace(perc, Subspace):
						if not Silent:
							print("Intervention:", S)
							print("Percolation:", perc)
						CS.append(S)
	return CS


def control_strategies_percolation_to_trapspace(Primes, Subspace, UseAttractors=False, Attractors=None, Limit=3, MaxOutputTrapspaces=1000000, Silent=False, StartingLength=0, PreviousCS=None, AvoidNodes=None):
	"""
	Computes control strategies for *Subspace* using trap spaces.
	It does not check that the elements of *Attractors* are attractors.
	It does not check that the elements of *PreviousCS* are control strategies.
	**arguments**:
		* *Primes*: prime implicants.
		* *Suspace* (dict): subspace.
		* *UseAttractors* (bool): use attractors to select trap spaces. Default value: False.
		* *Attractors* (list): list of complex attractors. A complex attractor is expected as a list of states (dicts). Only used when *UseAttractors* is True. Default value: empty list. 
		* *Limit* (int): maximal size of the control strategies. Default value: 3.
		* *MaxOutput* (int): maximal number of trap spaces that are calculated. Default value: 1000000.
		* *Silent* (bool): not print infos to screen. Default value: False.
		* *StartingLength* (int): minimal size of the control strategies. Default value: 0.
		* *PreviousCS* (list): list of already identified control strategies. Default value: empty list.
		* *AvoidNodes* (list): list of nodes that cannot be part of the control strategies. Default value: empty list.
	**returns**:
		* *CS* (list): list of control strategies (dict) of *Subspace* obtained via the selected trap spaces.
	**example**::
		>>> controlStrategies_percolating_to_trapspace(primes, {'v1': 1})
	"""

	if not Attractors:
		Attractors = []
	if not PreviousCS: 
		PreviousCS = []
	if not AvoidNodes:
		AvoidNodes = []
	
	# Selecting trap spaces
	tspacesAll = trapspaces_intersecting_subspace(Primes, Subspace, "percolated", MaxOutputTrapspaces)
	if {} not in tspacesAll: tspacesAll.append({})
	tsmin = PyBoolNet.AspSolver.trap_spaces(Primes, "min")
	selTS = select_trapspaces(tspacesAll, Subspace, UseAttractors, tsmin, Attractors)

	# Selecting intervention candidates
	selTS_values = dict()
	for x in selTS:
		for y in x.keys():
			if not y in AvoidNodes:
				if y in selTS_values.keys():
					if not x[y] in selTS_values[y]:
						selTS_values[y].append(x[y])
				else:
					selTS_values[y] = [x[y]]
	
	# Identifying control strategies
	CS = PreviousCS
	for i in range(StartingLength, Limit+1):
		if not Silent: print("Checking control strategies of size",i)
		for vs in itertools.combinations(selTS_values.keys(),i):
			# Consider all consistent combinations
			subsets = itertools.product(*[selTS_values[x] for x in vs])
			for ss in subsets:
				S = dict(zip(vs,ss))
				if not any(is_included_in_subspace(S,x) for x in CS):
					perc = PyBoolNet.AspSolver.percolate_trapspace(Primes,S)
					if any((is_included_in_subspace(perc, T) and is_included_in_subspace(T,S)) for T in selTS):
						if not Silent:
							print("Intervention:", S)
							print("Percolation:", perc)
						CS.append(S)
	return CS


def results_info(CS):
	"""
	Returns a text stating the amount and size of the control strategies in *CS*.
	**arguments**:
		* *CS*: list of control strategies.
	**returns**:
		* *text* (string): text stating the number and size of the elements in *CS*.
	**example**::
		>>> results_info([{'v1': 1}, {'v2':0, 'v3':1}])
	"2 control strategies, 1 of size 1, 1 of size 2"
	"""
	
	text = str(len(CS)) + " control strategies"
	sizes = [len(x) for x in CS]
	CS_sizes = list({(el, sizes.count(el)) for el in sizes})
	CS_sizes.sort()
	for x in CS_sizes:
		text = text + ", " + str(x[1]) + " of size " + str(x[0])
	return text
