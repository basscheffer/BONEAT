import numpy as np
import dateutil.parser as dp

path = r"data\npy_data\AUDUSD240_NormData.npy"
s_date = "2001-01-01"
e_date = "2004-01-01"

A = np.load(path)

from_date=dp.parse(s_date)
to_date=dp.parse(e_date)
idx=(A[:,0]>=from_date) & (A[:,0]<to_date)
print(A[idx])