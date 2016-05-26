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

    def testPopulation(self):
        print "\nGeneration %i, %i species ,%i innovations"\
              %(self.generation,len(self.species.l_species),len(self.innovations.l_innovations))
        sim.fastSimulate(self.species.getAllGenomes(),'testdata.npy')

    def evolvePopulation(self):

        # test te previous population for fitness
        self.testPopulation()
        #remove weakest individuals from species and stale speces
        self.species.removeWeakPopulation()
        #breed children and fill new population
        self.species.breedChildren(self.innovations)
        self.generation+=1

if __name__=='__main__':
    time.clock()
    p = Pool(4)
    for i in range(10):
        p.evolvePopulation()
        print 'duration: ',time.clock()