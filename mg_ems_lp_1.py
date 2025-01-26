# Microgrid Optimization using Pyomo and GLPK
# Minimizes imbalance between generation and load over 24-hour horizon

import pyomo.environ as pyo
import numpy as np
import matplotlib.pyplot as plt
import sys

# Create a concrete model
model = pyo.ConcreteModel()
    
# Optimization horizon
horizon = 24
    
# Battery parameters
max_capacity = 10.0  # Maximum battery capacity
initial_soc = 0.5    # Initial state of charge
    
# PV generation (normalized, 0-1 scale)
pv_generation = [0, 0, 0, 0, 0, 0, 0.15, 0.27, 0.44, 0.65, 0.84, 0.97, 0.996, 0.91, 0.75, 0.54, 0.35, 0.20, 0, 0, 0, 0, 0, 0]

# Load demand (normalized, 0-1 scale)
load_demand = [0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.4, 0.7, 0.7, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8, 0.8, 0.8, 0.4, 0.4, 0.4, 0.2]

# Decision variables for each time step
model.battery_output = pyo.Var(range(horizon), domain=pyo.Reals)
model.imbalance_pos = pyo.Var(range(horizon), domain=pyo.NonNegativeReals)
model.imbalance_neg = pyo.Var(range(horizon), domain=pyo.NonPositiveReals)
    
# Objective function: Minimize sum of imbalance
def imbalance_objective_rule(model):
    return sum(model.imbalance_pos[t] - model.imbalance_neg[t] for t in range(horizon))
model.objective = pyo.Objective(rule=imbalance_objective_rule, sense=pyo.minimize)
    
# Constraints
# Imbalance (positive) constraint
def imbalance_pos_constraint_rule(model, t):
    return model.imbalance_pos[t] == pv_generation[t] + model.battery_output[t] - load_demand[t]
model.imbalance_pos_constraint = pyo.Constraint(range(horizon), rule=imbalance_pos_constraint_rule)

# Imbalance (negative) constraint
def imbalance_neg_constraint_rule(model, t):
    return model.imbalance_neg[t] == pv_generation[t] + model.battery_output[t] - load_demand[t]
model.imbalance_neg_constraint = pyo.Constraint(range(horizon), rule=imbalance_neg_constraint_rule)

# Solve the optimization problem
solverName = 'glpk'
solverPathFolder = 'C:\\winglpk-4.65\\glpk-4.65\\w64'
solverPathExe = 'C:\\winglpk-4.65\\glpk-4.65\\w64\\glpsol'
sys.path.append(solverPathFolder)
solver = pyo.SolverFactory(solverName, executable = solverPathExe)
results = solver.solve(model)
    
# Extract results
battery_results = [model.battery_output[t]() for t in range(horizon)]
imbalance_pos_results = [model.imbalance_pos[t]() for t in range(horizon)]
imbalance_neg_results = [model.imbalance_neg[t]() for t in range(horizon)]

# Calculate battery state-of-charge
battery_soc = [initial_soc]
for output in battery_results:
    # Simple state of charge calculation
    new_soc = battery_soc[-1] - output / max_capacity
    battery_soc.append(new_soc)
    
# Plotting
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10,5), sharex=True, height_ratios=[2, 1, 1])
    
# First subplot: Power outputs
ax1.plot(range(horizon), pv_generation, label='PV', linestyle='--')
ax1.plot(range(horizon), load_demand, label='Load', linestyle='--')
ax1.plot(range(horizon), battery_results, label='Battery')
ax1.set_ylabel('Power [kW]')
ax1.legend()
ax1.grid()

# Second subplot: Imbalance constraints
ax2.plot(range(horizon), imbalance_pos_results, label='Pos. imbalance', color='blue')
ax2.plot(range(horizon), imbalance_neg_results, label='Neg. imbalance', color='blue')
ax2.set_ylabel('Power [kW]')
ax2.legend()
ax2.grid()

# Third subplot: Battery state-of-charge
ax3.plot(range(horizon+1), battery_soc, label='Battery SOC', color='red')
ax3.set_xlabel('Time step')
ax3.set_ylabel('SOC [-]')
ax3.legend()
ax3.grid()

plt.tight_layout()
plt.show()