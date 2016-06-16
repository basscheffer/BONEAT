from pool import *
import pickle

if __name__=='__main__':

    p = Pool("data/config_files/AUDUSD240.cfg")
    for i in range(40):
        p.evolvePopulation()
        # pickle.dump(p,open("longtest.p","w"))
