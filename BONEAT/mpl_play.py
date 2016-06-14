import numpy as np
import pylab as plt

Y = [[3,4,5,6],[2,2,2,2],[1,2,3,1]]

X = range(4)

plt.stackplot(X, Y, baseline="zero")
plt.show()