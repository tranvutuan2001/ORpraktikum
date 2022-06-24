# -*- coding: utf-8 -*-

import gurobipy as gp
from gurobipy import GRB


#initialize the tuplelist x[tuple]->value

l=gp.tuplelist([(1,1,1),(1,7,2),(6,7,8)]) #house i,model m,time t
print("Tuplelist l=")
print(l)

x={}
for i in l:
    x[i]=7+i[-1]
print("--------------------\nx=")
for tuple in x:
    print(tuple,":",x[tuple])    





print("--------------------\nOnly select tuples with i=1")
print(l.select(1,"*","*"))


indexes_houses=set([k[0] for k in l]) #unique house indexes
print("indexes houses=",indexes_houses)

indexes_models=set(k[1] for k in l) #unique models
print("indexes_model=",indexes_models)

indexes_time=set(k[2] for k in l)
print("indexes_time=",indexes_time)



print("-------------\nGroup by Housetype")
q_i={}
for house in indexes_houses:  
    q_i[house]=sum([x[i] for i in l.select(house,"*","*")])
print(q_i)       


print("---------\nGroup by Model")
q_m={}
for model in indexes_models: #for all m in Models
    q_m[model]=sum([x[i] for i in l.select("*",model,"*")]) #sum over all tuples with m=model
print(q_m)

#calc time * cost
print("sum of costs:")
print(sum(x[i]*i[2] for i in l.select()))



