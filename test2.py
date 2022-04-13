import numpy as np
a = np.array([[10, 20, 30, 40, 50],
              [ 6,  7,  8,  9, 10]])
permutation = [0, 4, 1, 3, 2]
idx = np.empty_like(permutation)
idx[permutation] = np.arange(len(permutation))

a[:] = a[:, idx]  # in-place modification of a

print(a)