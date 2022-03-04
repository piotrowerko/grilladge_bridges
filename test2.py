# import numpy as np

# a = np.array([1, 0, 0, 0])
# print(a)
# b = np.array([1, 2, 3])

# # #c = np.array([])

# # # c = np.append(a, b, axis=None)
# # # print(c)

# # d = np.vstack(a,b)


# def my_fun(a, b, c, d):
#     return a + b + c + d

# my_tuple = (1, 1, 1, 1)

# print(my_fun(*my_tuple))


# from PyNite import FEModel3D

# wd185_fe = FEModel3D()
# # Define the nodes
# print(wd185_fe.add_node(*a))

import numpy as np
a = np.array([[10, 20, 30, 40, 50],
              [ 6,  7,  8,  9, 10]])
permutation = [0, 4, 1, 3, 2]
idx = np.empty_like(permutation)
idx[permutation] = np.arange(len(permutation))

a[:] = a[:, idx]  # in-place modification of a

print(a)