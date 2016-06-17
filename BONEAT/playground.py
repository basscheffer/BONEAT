# import csv
#
# nf = open("data/ga_logs/AUDUSD240xl.csv","w")
# writer = csv.writer(nf,delimiter=",",quotechar='"')
#
# with open("data/ga_logs/AUDUSD240.csv","r") as of:
#     reader = csv.reader(of,delimiter=",",quotechar='"')
#     for row in reader:
#         if row:
#             writer.writerow(row[:5])
#
# import numpy as np
# import genome
# import phenotype
# import simulate
# import dateutil.parser as dp
#
# A = np.load("data/npy_data/AUDUSD240_NormData.npy")
#
# from_date=dp.parse("2007-01-01")
# to_date=dp.parse("2013-01-01")
# # idx=(A[:,0]>=from_date) & (A[:,0]<to_date)
# # data1 = A[idx]
# # print data1
# si = min(np.where(A[:,0]>=from_date)[0])
# ei = min(np.where(A[:,0]>=to_date)[0])
# data = A[si:ei]
#
# settings = {"spread":"1.8","profit_norm":0.627450}
# G = genome.buildFromGTFile("data/genotypes/AUDUSD240.gt.txt")
# NN = phenotype.neuralNetwork(G)
# SIM = simulate.Simulator()
# print SIM.runSimulation(data,NN,settings)

import pickle
import species
import random
import cProfile

p = pickle.load(open("longtest.p","r"))
G = random.choice(p.species.getAllGenomes())
pr = cProfile.Profile()
pr.enable()
G.mutate(p.innovations)
pr.print_stats("tottime")

