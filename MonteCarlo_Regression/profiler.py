import cProfile
import pstats

def profile_calculate_at_numH():
    # calculate_at_numH(10)  # Run with a small number of steps for profiling
    pass

cProfile.run('profile_calculate_at_numH()', 'restats')
p = pstats.Stats('restats')
p.sort_stats('cumulative').print_stats(10)
