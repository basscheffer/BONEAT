from innovation import *
from genome import *
from species import *
import phenotype as phen
import simulate as sim
import time

class Pool:

    def __init__(self,population,pair="",time_frame=1,processors=4):

        self.population = population

        self.species = SpeciesList(self.population)
        self.innovations = innovList()
        self.newPopulation()
        self.generation = 1
        self.processors = processors
        self.df_path = "data/"+pair+str(time_frame)+"_NormData.npy"

    def newPopulation(self):

        for i in range(self.population):
            nG = newSimpleGenome(9,3,self)
            self.species.addToSpecies(nG)

    def testPopulation(self):
        print "\nGeneration %i, %i species ,%i innovations"\
              %(self.generation,len(self.species.l_species),len(self.innovations.l_innovations))
        if self.processors > 1:
            sim.fastSimulate(self.species.getAllGenomes(),self.df_path,self.processors)
        else:
            sim.slowSimulate(self.species.getAllGenomes(),self.df_path)

    def evolvePopulation(self):

        # test te previous population for fitness
        self.testPopulation()
        #remove weakest individuals from species and stale speces
        self.species.removeWeakPopulation()
        #breed children and fill new population
        self.species.breedChildren(self.innovations)
        self.generation+=1

if __name__=='__main__':

    p = Pool(300,pair="AUDUSD",time_frame=240,processors=4)
    for i in range(20):
        p.evolvePopulation()

