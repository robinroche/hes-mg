# Microgrid Simple Energy Management
# Uses simple rule-based battery management

import numpy as np
import matplotlib.pyplot as plt

# Optimization horizon
horizon = 24

# Battery parameters
max_capacity = 10.0  # Maximum battery capacity
initial_soc = 0.5    # Initial state of charge
    
# PV generation (normalized, 0-1 scale)
pv_generation = [0, 0, 0, 0, 0, 0, 0.15, 0.27, 0.44, 0.65, 0.84, 0.97, 0.996, 0.91, 0.75, 0.54, 0.35, 0.20, 0, 0, 0, 0, 0, 0]

# Load demand (normalized, 0-1 scale)
load_demand = [0.2, 0.2, 0.2, 0.2, 0.2, 0.4, 0.4, 0.7, 0.7, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8, 0.8, 0.8, 0.4, 0.4, 0.4, 0.2]

battery_results = []
battery_soc = [initial_soc]

# Simple rule-based battery management
for t in range(horizon):
    # Calculate power imbalance (generation - demand)
    power_imbalance = pv_generation[t] - load_demand[t]
    if power_imbalance > 0:
        # Excess generation: charge battery
        battery_output = power_imbalance
    else:
        # Insufficient generation: discharge battery
        battery_output = power_imbalance
    battery_results.append(battery_output)
    
    # Update battery state-of-charge
    new_soc = battery_soc[-1] + battery_output / max_capacity
    battery_soc.append(new_soc)
    
# Plotting
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10,5), sharex=True)
    
# First subplot: Power outputs
ax1.plot(range(horizon), pv_generation, label='PV', linestyle='--')
ax1.plot(range(horizon), load_demand, label='Load', linestyle='--')
ax1.plot(range(horizon), battery_results, label='Battery')
ax1.set_ylabel('Power [kW]')
ax1.legend()
ax1.grid()

# Second subplot: Battery state-of-charge
ax2.plot(range(horizon+1), battery_soc, label='Battery SOC', color='red')
ax2.set_xlabel('Time step')
ax2.set_ylabel('SOC [-]')
ax2.legend()
ax2.grid()

plt.tight_layout()
plt.show()