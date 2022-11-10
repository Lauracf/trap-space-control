% Percolation set up - node control

goal(T,S) :- goal(Z,T,S), Z < 0.
satisfy(V,W,S) :- formula(W,D); dnf(D,C); clause(C,V,S).
closure(V,T)   :- goal(V,T).
closure(V,S*T) :- closure(W,T); satisfy(V,W,S); not goal(V,-S*T).
{ node(V,S) } :- closure(V,S), not avoid_node(V), satisfied(Z), Z < 0.


% Percolation set up for trap spaces - node control

{ node(V,S) : goal(Z,V,S), not avoid_node(V), satisfied(Z), subspace(Z), Z >= 0}.


%% Percolation set up - edge control

{ edge(Vi,Vj,1); edge(Vi,Vj,-1) } :- formula(Vj,D), dnf(D,C), clause(C, Vi, S), not avoid_edge(Vi,Vj), satisfied(Z), Z < 0.
{ edge(Vi,Vj,1); edge(Vi,Vj,-1) } :- formula(Vj,D), dnf(D,C), clause(C, Vi, S), not avoid_edge(Vi,Vj), goal(Z,Vj,T), satisfied(Z), subspace(Z), Z >= 0.
   

% Restrictions on interventions

:- node(V,S), node(V,-S).
:- edge(Vi,Vj,S), edge(Vi, Vj, -S).
:- node(V,S), edge(V,Vj).
:- node(V), edge(Vi,V).

node(V) :- node(V,S).
edge(Vi,Vj) :- edge(Vi,Vj,S).


%% Apply edge interventions

new_clause(C,V,S) :- clause(C,V,S); dnf(D,C); formula(Vj,D); not edge(V,Vj).
remove_dnf(D,C):- clause(C,Vi,-S); edge(Vi,Vj,S); dnf(D,C); formula(Vj,D).
new_dnf(D,C) :- new_clause(C,Vi,S); dnf(D,C); formula(Vj,D); not remove_dnf(D,C).
remove_formula(Vj,D) :- dnf(D,C); formula(Vj,D); edge(Vi,Vj,S) : clause(C,Vi,S).
new_formula(V,D) :- new_dnf(D,C); formula(V,D); not remove_formula(V,D).

fixed_node(V,1) :- remove_formula(V,D).
fixed_node(V,-1) :- not remove_formula(V,D); not new_formula(V,D); formula(V,D).


%% Get total interventions

intervention(V,S) :- node(V,S).
intervention(V,S) :- not node(V,S), not node(V,-S), fixed_node(V,S).
intervention(V) :- intervention(V,S).


%% Iterative percolation

eval_formula(Z,V,S) :- subspace(Z); intervention(V,S).
free(Z,V,D) :- new_formula(V,D); subspace(Z); not intervention(V).

eval_clause(Z,C,-1) :- new_clause(C,V,S); eval_formula(Z,V,-S).
eval_formula(Z,V, 1) :- free(Z,V,D); eval_formula(Z,W,T) : new_clause(C,W,T); new_dnf(D,C).
eval_formula(Z,V,-1) :- free(Z,V,D); eval_clause(Z,C,-1) : new_dnf(D,C).


%% Satisfaction requirements

not satisfied(Z) :- goal(Z,T,S), not eval_formula(Z,T,S), subspace(Z).
satisfied(Z) :- eval_formula(Z,T,S) : goal(Z,T,S); subspace(Z).
0 < { satisfied(Z) : subspace(Z) }.


%% Size requirements

:- maxsize>0; maxsize + 1 { node(V,R); edge(Vi,Vj,S) }.
:- maxnodes<0; 1 { node(V,S) }.
:- maxedges<0; 1 { edge(Vi,Vj,S) }.


#show node/2.
#show edge/3.
