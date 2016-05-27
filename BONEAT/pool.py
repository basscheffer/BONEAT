from innovation import *
from genome import *
from species import *
import phenotype as phen
import simulate as sim
import time



class Pool:

    def __init__(self,population):

        self.population = population

        self.species = SpeciesList(self.population)
        self.innovations = innovList()
        self.newPopulation()
        self.generation = 1

    def newPopulation(self):

        for i in range(self.population):
            nG = newSimpleGenome(9,3,self)
            self.species.addToSpecies(nG)

    def testPopulation(self,processors = 4):
        print "\nGeneration %i, %i species ,%i innovations"\
              %(self.generation,len(self.species.l_species),len(self.innovations.l_innovations))
        if processors > 1:
            sim.fastSimulate(self.species.getAllGenomes(),'data/AUDUSD4H_NPA_15Y',processors)
        else:
            sim.slowSimulate(self.species.getAllGenomes(),'data/AUDUSD4H_NPA_15Y')

    def evolvePopulation(self):

        # test te previous population for fitness
        self.testPopulation(4)
        #remove weakest individuals from species and stale speces
        self.species.removeWeakPopulation()
        #breed children and fill new population
        self.species.breedChildren(self.innovations)
        self.generation+=1

if __name__=='__main__':
    # import numpy as np

    p = Pool(50)
    for i in range(20):
        p.evolvePopulation()

    # genome = p.species.l_species[0].l_genomes[2]
    # for i in range(3):
    #     print "------------------",i,"-----------------"
    #
    #     dataset = np.load('testdata.npy')[:10]
    #     NN = phen.neuralNetwork(genome)
    #     for r in dataset:
    #         il = [0,0,0]
    #         il.extend(r)
    #         print NN.update(il)

