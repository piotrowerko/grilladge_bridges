# # importing the module
import numpy as np
  
# # creating an array
# arr = np.array([3, 30, 30, 30])
# print('Original Array : ', arr)
  
# # appending to the array
# arr = np.append(arr, [7])
# # print('Array after appending : ', arr)

# import math
# print(math.radians(90))

# print(np.sum(arr[0:2]))

# ppp = [3, 30, 30, 30]

# print(sum(ppp[1:4]))

# for i in range(0,3,1):
#     print(i)

# __list = 6* [True]
# print(__list)

data = np.array([[11, 22, 33],
		[44, 55, 66],
		[77, 88, 99]])
# separate data
# X, y = data[:, :-1], data[:, -1]
# print(X)
# print(y)

X = np.vstack(data[:, 1:-1])
print(X)