from Control import *
from pprint import pformat

if __name__=="__main__":

	## Reading network

	bnet = "Networks/grieco_mapk.bnet"
	primes = PyBoolNet.FileExchange.bnet2primes(bnet)

	## Setting parameters

	type_CS = "both" # options: via_trapspaces, percolation_only, both
	phenotype = {"Apoptosis":1,"Proliferation":0,"Growth_Arrest":1}
	avoid_nodes = ["Apoptosis","Proliferation","Growth_Arrest"]
	limit = 4
	use_attractors = True
	complex_attractors = []
	comments = True
	output_file = "Results/grieco_lim" + str(limit) + "_" + type_CS

        
	## Computing control strategies

	if type_CS in {"percolation_only","both"}:
		CS_percolation_only = control_strategies_percolation_only(primes, phenotype, limit, Silent = not comments, AvoidNodes = avoid_nodes)

	if type_CS in {"via_trapspaces","both"}:
		CS_via_trapspaces = control_strategies_percolation_to_trapspace(primes, phenotype, use_attractors, complex_attractors, limit, Silent = not comments, AvoidNodes = avoid_nodes)


	## Saving output

	if comments:
		print("Phenotype = " + pformat(phenotype) + "\n")
		if type_CS in {"percolation_only","both"}: print("Percolation only:", results_info(CS_percolation_only))
		if type_CS in {"via_trapspaces","both"}: print("Via trapspaces:", results_info(CS_via_trapspaces))

	with open(output_file+".txt", "w") as f:
		f.write("Phenotype = " + pformat(phenotype) + "\n")
		if type_CS in {"percolation_only","both"}: f.write("#Control strategies percolation only" + "\nCS_per = " + pformat(CS_percolation_only) + "\n")
		if type_CS in {"via_trapspaces","both"}: f.write("#Control strategies via trapspaces" + "\nCS_ts = " + pformat(CS_via_trapspaces) + "\n")
		
