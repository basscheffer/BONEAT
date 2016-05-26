import multiprocessing as mp
import random
import numpy

def square(fp):

    data = numpy.load(fp)
    sum = 0.0
    for r in data:
        sum += r[3]

    return sum



if __name__ == '__main__':

    fpl = ['testdata.npy']*100
    pool = mp.Pool(4)
    res = pool.map(square,fpl,3)
    pool.close()
    pool.join()
    for r in res:
        print r