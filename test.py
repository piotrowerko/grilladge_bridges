# # importing the module
import numpy as np
  

data = np.array([[11, 22, 33],
		[44, 55, 66],
		[77, 88, 99]])


X = np.vstack(data[:, 1:-1])
print(X)