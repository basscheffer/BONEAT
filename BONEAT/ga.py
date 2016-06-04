from pool import *

if __name__=='__main__':

    p = Pool("data/config_files/AUDUSD240.cfg")
    p.testPopulation()
    for i in range(40):
        p.evolvePopulation()
