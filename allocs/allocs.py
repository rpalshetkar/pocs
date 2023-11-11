from collections import defaultdict

import pandas as pd
from pulp import (
    LpAffineExpression, LpConstraint, LpConstraintLE, LpMaximize, LpProblem,
    LpStatus, LpVariable, lpSum
)

rdf = pd.read_csv('csvs/people.csv')
rdf = rdf.set_index('resource').sort_index()

opdf = pd.read_csv('csvs/projects.csv')
opdf = pd.melt(
    opdf,
    id_vars=['project', 'budget'],
    value_vars=['car1', 'car2', 'car3', 'car4', 'car5', 'car6'],
    var_name='car',
    value_name='pct'
)
opdf['p_car'] = opdf['project'] + '_' + opdf['car']
opdf['funding'] = opdf['pct'] * opdf['budget']
opdf = opdf[opdf['funding'] != 0.0].set_index('p_car').sort_index()
pdf = opdf[['funding']]
prob = LpProblem("Allocation Problem", LpMaximize)
# Create the decision variables
variables = {}
for p_car in opdf.index:
    for resource in rdf.index:
        if rdf.loc[resource, 'car'] not in p_car:
            continue
        varx = f"{p_car}_{resource}"
        variable_name = f"alloc_{varx}"
        variables[varx] = LpVariable(
            variable_name, lowBound=0, upBound=1, cat='Continuous'
        )

# Accessing the decision variables
for vx in variables:
    print(f"Decision Variable: {vx}")

car_vars = defaultdict(list)
res_vars = defaultdict(list)

for vx in variables:
    proj, car, res = vx.split('_')
    p_car = f"{proj}_{car}"
    res_funding = rdf.loc[res, "funding"]
    car_vars[p_car].append((variables[vx], res_funding))
    res_vars[res].append((variables[vx], res_funding))

for car, vxs in car_vars.items():
    constraint = f"constr_car_{car}"
    funding = pdf.loc[car, "funding"]
    sum_expr = LpAffineExpression(vxs)
    constraint = LpConstraint(e=sum_expr, sense=LpConstraintLE, rhs=funding)
    prob += constraint

for res, vxs in res_vars.items():
    constraint = f"constr_res_{res}"
    funding = rdf.loc[res, "funding"]
    sum_expr = LpAffineExpression(vxs)
    constraint = LpConstraint(e=sum_expr, sense=LpConstraintLE, rhs=funding)
    prob += constraint

print(prob)

prob += lpSum([variables[var] for var in variables])

prob.solve()
print("Status:", LpStatus[prob.status])
print("Optimal values:")
allocs = []
for var, val in variables.items():
    proj, car, res = var.rsplit('_')
    funding = rdf.loc[res, "funding"]
    weight = val.value()
    allocs.append({
        'project': proj,
        'car': car,
        'resource': res,
        'card': funding,
        'alloc': funding * weight,
    })
    print(f"{var}=> {weight}")

print(pd.pivot_table(opdf, index='project', values=['budget'], aggfunc='sum'))
adf = pd.DataFrame(allocs)
for fld in ['project', 'car', 'resource']:
    print(pd.pivot_table(adf, index=fld, values=['alloc'], aggfunc='sum'))
