# https://or.stackexchange.com/questions/8773/how-do-i-solve-a-probability-based-knapsack-problem
# https://or.stackexchange.com/questions/3952/are-python-and-julia-used-for-optimization-in-industry


# 1. Find lineup with highest probability for super-high value
# - Maybe put every player's outcome in the 90th percentile, do regular knapsack, optimize from there
# 2. go down X points, find optimal lineup for that lower total value
# 3. Do a bunch of simulations, see which lineup has the highest win rate, return that
