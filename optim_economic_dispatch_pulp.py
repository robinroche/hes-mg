import pulp
import pandas as pd
import matplotlib.pyplot as plt

# Create the optimization problem
prob = pulp.LpProblem("Power_System_Optimization", pulp.LpMinimize)

# Define parameters
num_generators = 3
demand = 1000  # MW
max_capacity = {1: 500, 2: 600, 3: 400}  # MW
min_capacity = {1: 100, 2: 100, 3: 50}   # MW
costs = {1: 20, 2: 25, 3: 30}  # $/MWh

# Define decision variables
generation = pulp.LpVariable.dicts("Gen", range(1, num_generators+1), 
                                   lowBound=0)  # Remove specific bounds here

# Add individual capacity constraints
for i in range(1, num_generators+1):
    prob += generation[i] >= min_capacity[i], f"Min_Capacity_Gen_{i}"
    prob += generation[i] <= max_capacity[i], f"Max_Capacity_Gen_{i}"

# Define objective function
prob += pulp.lpSum(generation[i] * costs[i] for i in range(1, num_generators+1)), "Total Cost"

# Add demand constraint
prob += pulp.lpSum(generation[i] for i in range(1, num_generators+1)) == demand, "Demand Balance"

# Solve the problem
prob.solve()

# Check the status
print(f"Status: {pulp.LpStatus[prob.status]}")

# Display and analyze results
def display_results(prob, generation):
    print("\nOptimal Solution:")
    for i in range(1, num_generators+1):
        print(f"Generator {i}: {generation[i].varValue:.2f} MW")
    print(f"\nTotal Cost: ${pulp.value(prob.objective):.2f}")

    # Create a DataFrame for easy analysis
    results_df = pd.DataFrame({
        'Generator': [f'Gen_{i}' for i in range(1, num_generators+1)],
        'Generation (MW)': [generation[i].varValue for i in range(1, num_generators+1)],
        'Cost ($/MWh)': [costs[i] for i in range(1, num_generators+1)]
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
display_results(prob, generation)
