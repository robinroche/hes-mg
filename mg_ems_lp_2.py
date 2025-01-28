# Microgrid Optimization with Enhanced Battery and PV Management

import pyomo.environ as pyo
import numpy as np
import matplotlib.pyplot as plt
import sys

# Create a concrete model
model = pyo.ConcreteModel()
    
# Optimization horizon
horizon = 24
    
# Battery parameters
max_capacity = 3.0    # Maximum battery capacity (kWh)
initial_soc = 0.5      # Initial state of charge
min_soc = 0.1          # Minimum state of charge
max_soc = 1          # Maximum state of charge
charge_efficiency = 0.9  # Battery charging efficiency
discharge_efficiency = 0.9  # Battery discharging efficiency
max_charge_rate = 0.3 * max_capacity  # Maximum charging rate per hour
max_discharge_rate = 0.3 * max_capacity  # Maximum discharging rate per hour
    
# PV generation (normalized, 0-1 scale)
pv_generation = [0, 0, 0, 0, 0, 0, 0.15, 0.27, 0.44, 0.65, 0.84, 0.97, 0.996, 0.91, 0.75, 0.54, 0.35, 0.20, 0, 0, 0, 0, 0, 0]

# Load demand (normalized, 0-1 scale)
load_demand = [0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.4, 0.7, 0.7, 0.4, 0.4, 0.4, 0.2, 0.4, 0.4, 0.2, 0.2, 0.8, 0.8, 0.8, 0.4, 0.4, 0.4, 0.2]

# Decision variables for each time step
model.battery_charge = pyo.Var(range(horizon), domain=pyo.NonNegativeReals, bounds=(0, max_charge_rate))
model.battery_discharge = pyo.Var(range(horizon), domain=pyo.NonNegativeReals, bounds=(0, max_discharge_rate))
model.is_charging = pyo.Var(range(horizon), domain=pyo.Binary)
model.curtailed_pv = pyo.Var(range(horizon), domain=pyo.NonNegativeReals)
model.load_shedding = pyo.Var(range(horizon), domain=pyo.NonNegativeReals)
model.battery_soc = pyo.Var(range(horizon+1), domain=pyo.Reals, bounds=(min_soc, max_soc))

# Battery charge/discharge constraints using a binary variable
def battery_charge_constraint(model, t):
    return model.battery_charge[t] <= max_charge_rate * model.is_charging[t]
model.battery_charge_constraint = pyo.Constraint(range(horizon), rule=battery_charge_constraint)

def battery_discharge_constraint(model, t):
    return model.battery_discharge[t] <= max_discharge_rate * (1 - model.is_charging[t])
model.battery_discharge_constraint = pyo.Constraint(range(horizon), rule=battery_discharge_constraint)

# Initial SOC constraint
def initial_soc_constraint_rule(model):
    return model.battery_soc[0] == initial_soc
model.initial_soc_constraint = pyo.Constraint(rule=initial_soc_constraint_rule)

def battery_soc_constraint_rule(model, t):
    # SOC evolution considering charging and discharging efficiencies
    return model.battery_soc[t+1] == model.battery_soc[t] + \
           (model.battery_charge[t] * charge_efficiency - \
            model.battery_discharge[t] / discharge_efficiency) / max_capacity
model.battery_soc_constraint = pyo.Constraint(range(horizon), rule=battery_soc_constraint_rule)

# Power balance constraint
def power_balance_constraint_rule(model, t):
    return (pv_generation[t] - model.curtailed_pv[t] + model.battery_discharge[t] - model.battery_charge[t] - load_demand[t] + model.load_shedding[t] == 0)
model.power_balance_constraint = pyo.Constraint(range(horizon), rule=power_balance_constraint_rule)

# Objective function: Minimize load shedding and PV curtailment
def objective_rule(model):
    return sum(10 * model.load_shedding[t] + model.curtailed_pv[t] for t in range(horizon))
model.objective = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

# Solve the optimization problem
solverName = 'glpk'
solverPathFolder = 'C:\\winglpk-4.65\\glpk-4.65\\w64'
solverPathExe = 'C:\\winglpk-4.65\\glpk-4.65\\w64\\glpsol'
sys.path.append(solverPathFolder)
solver = pyo.SolverFactory(solverName, executable=solverPathExe)
results = solver.solve(model)
    
# Extract results
battery_charge_results = [model.battery_charge[t]() for t in range(horizon)]
battery_discharge_results = [model.battery_discharge[t]() for t in range(horizon)]
battery_soc_results = [model.battery_soc[t]() for t in range(horizon+1)]
curtailed_pv_results = [model.curtailed_pv[t]() for t in range(horizon)]
load_shedding_results = [model.load_shedding[t]() for t in range(horizon)]
is_charging_results = [model.is_charging[t]() for t in range(horizon)]

# Print summary statistics
print("Total PV Curtailment:", sum(curtailed_pv_results))
print("Total Load Shedding:", sum(load_shedding_results))
print("Total Battery Charge:", sum(battery_charge_results))
print("Total Battery Discharge:", sum(battery_discharge_results))
print("Initial Battery SOC:", model.battery_soc[0]())
print("Final Battery SOC:", model.battery_soc[horizon]())
print("Charging status over time:")
print([1 if x > 0.5 else 0 for x in is_charging_results])

# Plotting
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10,5), sharex=True, height_ratios=[2, 1, 1])
    
# First subplot: Power generation and demand
ax1.plot(range(horizon), pv_generation, label='PV generation', linestyle='--')
ax1.plot(range(horizon), load_demand, label='Demand', linestyle='--')
ax1.plot(range(horizon), battery_discharge_results, label='Battery discharge')
ax1.plot(range(horizon), battery_charge_results, label='Battery charge')
ax1.set_ylabel('Power [kW]')
ax1.legend()
ax1.grid()
ax1.set_title('Power generation and demand')

# Second subplot: PV Curtailment and Load Shedding
ax2.plot(range(horizon), curtailed_pv_results, label='PV curtailment', color='green')
ax2.plot(range(horizon), load_shedding_results, label='Load shedding', color='orange')
ax2.set_ylabel('Power [kW]')
ax2.legend()
ax2.grid()
ax2.set_title('PV curtailment and load shedding')

# Third subplot: Battery state-of-charge
ax3.plot(range(horizon+1), battery_soc_results, label='Battery SOC', color='red')
ax3.set_ylabel('SOC [-]')
ax3.set_xlabel('Time [h]')
ax3.legend()
ax3.grid()
ax3.set_title('Battery state-of-charge')

plt.tight_layout()
plt.show()
