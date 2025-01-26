import pyomo.environ as pyo
import pandas as pd
import matplotlib.pyplot as plt
import sys


# Create a concrete model
model = pyo.ConcreteModel()

# Define parameters
model.gen_set = pyo.Set(initialize=[1, 2, 3])  # Set of generators
model.demand = pyo.Param(initialize=1000)  # MW
model.max_capacity = pyo.Param(model.gen_set, initialize={1: 500, 2: 600, 3: 400})  # MW
model.min_capacity = pyo.Param(model.gen_set, initialize={1: 100, 2: 100, 3: 50})   # MW
model.costs = pyo.Param(model.gen_set, initialize={1: 20, 2: 25, 3: 30})  # $/MWh

# Define decision variables
model.generation = pyo.Var(model.gen_set, bounds=lambda model, i: (model.min_capacity[i], model.max_capacity[i]))

# Define objective function
def objective_rule(model):
    return sum(model.generation[i] * model.costs[i] for i in model.gen_set)
model.objective = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

# Define constraints
def demand_rule(model):
    return sum(model.generation[i] for i in model.gen_set) == model.demand
model.demand_constraint = pyo.Constraint(rule=demand_rule)

# Solve the model
solverName = 'glpk'
solverPathFolder = 'C:\\winglpk-4.65\\glpk-4.65\\w64'
solverPathExe = 'C:\\winglpk-4.65\\glpk-4.65\\w64\\glpsol'
sys.path.append(solverPathFolder)
solver = pyo.SolverFactory(solverName, executable = solverPathExe)
results = solver.solve(model)

# Check solver status
print(f"Solver Status: {results.solver.status}")
print(f"Termination Condition: {results.solver.termination_condition}")

# Display and analyze results
def display_results(model):
    print("\nOptimal Solution:")
    for i in model.gen_set:
        print(f"Generator {i}: {pyo.value(model.generation[i]):.2f} MW")
    print(f"\nTotal Cost: ${pyo.value(model.objective):.2f}")

    # Create a DataFrame for easy analysis
    results_df = pd.DataFrame({
        'Generator': [f'Gen_{i}' for i in model.gen_set],
        'Generation (MW)': [pyo.value(model.generation[i]) for i in model.gen_set],
        'Cost ($/MWh)': [model.costs[i] for i in model.gen_set]
    })
    results_df['Total Cost ($)'] = results_df['Generation (MW)'] * results_df['Cost ($/MWh)']
    
    print("\nDetailed Results:")
    print(results_df)
    
    # Visualize results
    plt.figure(figsize=(10, 6))
    plt.bar(results_df['Generator'], results_df['Generation (MW)'])
    plt.title('Power Generation by Generator')
    plt.xlabel('Generator')
    plt.ylabel('Generation (MW)')
    plt.show()

# Call the function to display results
display_results(model)
