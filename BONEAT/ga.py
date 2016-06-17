from pool import *
import pickle
import cProfile
import pstats

if __name__=='__main__':

    p = Pool("data/config_files/AUDUSD240.cfg")
    for i in range(10000):
        # pr = cProfile.Profile()
        # pr.enable()
        p.evolvePopulation()
        # pr.create_stats()
        # ps = pstats.Stats(pr)
        # ps.sort_stats("cumtime")
        # ps.print_stats(.2)
        # ps.print_callers()

        pickle.dump(p,open("longtest.p","w"))
