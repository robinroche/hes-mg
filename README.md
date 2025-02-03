# hes-mg
Code for SPIM's course on hybrid energy systems (HES) - focus on microgrids
Used libraries and tools: numpy, pandas, pyomo, pulp, matplotlib, glpk

The following files are included:
- optim_economic_dispatch_pyomo.py: demonstrates the use of pyomo to solve a basic economic dispatch problem based on linear programming
- optim_economic_dispatch_pulp.py: same as above, but with pulp
- mg_ems_rb_1.py: demonstrates the use of simple rules to manage energy in an islanded microgrid including PV panels, a bbatery and a load, over an horizon of 24 hours
- mg_ems_lp_1.py: same as above but using linear programming and pyomo, without considering any battery constraint
- mg_ems_lp_2.py: same as above but while considering battery constraints

All Python scripts were tested on a Windows computer and ran successfully.
