import pygad
import numpy as np

"""
https://machinelearningmastery.com/simple-genetic-algorithm-from-scratch-in-python/
"""

n_bits = 8
#print(np.random.randint(0, 2, n_bits))

n_pop = 10
pop = [np.random.randint(0, 2, n_bits).tolist() for i in range(n_pop)]
#print(pop)

selection_index = np.random.randint(len(pop))
#print(selection_index)

k=3
pp = np.random.randint(0, len(pop), k-1)
print(pp)