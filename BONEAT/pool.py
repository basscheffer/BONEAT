from innovation import *
from genome import *
from species import *
import phenotype as phen
import simulate as sim
import time
import ConfigParser
import csv

class Pool:

    def __init__(self,cfg_filepath):

        self.getSettingsFromCfg(cfg_filepath)

        self.population = int(self.GS["population"])
        self.species = SpeciesList(self.GS)
        self.innovations = innovList()
        self.newPopulation()
        self.generation = 1
        self.processors = int(self.GS["cores"])

    def getSettingsFromCfg(self,cfg_filepath):
        config = ConfigParser.RawConfigParser()
        config.read(cfg_filepath)
        self.GS={}

        sections = config.sections()
        for sec in sections:
            d = dict(config.items(sec))
            self.GS.update(d)

        tf_dict = {"M5":5,"M15":15,"M30":30,"H1":60,"H4":240,"D1":1440}
        self.GS["timeframe"] = tf_dict[self.GS["timeframe"]]

        self.GS["test_data_path"] = "data/npy_data/{}{}_NormData.npy"\
            .format(self.GS["pair"],self.GS["timeframe"])

        np = "data/norm_fs/{}{}_NormConst.txt"\
            .format(self.GS["pair"],self.GS["timeframe"])
        with open(np) as f:
            for l in f:
                p = l.split(";")
                if p[0] == "P":
                    self.GS["profit_norm"] = float(p[1])

    def newPopulation(self):

        for i in range(self.population):
            nG = newSimpleGenome(9,3,self,self.GS)
            self.species.addToSpecies(nG)

    def testPopulation(self):
        print "\nGeneration %i, %i species ,%i innovations"\
              %(self.generation,len(self.species.l_species),len(self.innovations.l_innovations))
        sim.fastSimulate(self.species.getAllGenomes(),self.GS)
        self.logGenerationResults()

    def logGenerationResults(self):
        data = self.species.getGenerationData()
        csvpath="data/ga_logs/{}{}.csv".format(self.GS["pair"],self.GS["timeframe"])
        with open(csvpath,"a") as csvf:
            writer = csv.writer(csvf, delimiter=',',quotechar='"')
            for row in data:
                line = [self.generation]
                line.extend(row)
                writer.writerow(line)

    def evolvePopulation(self):

        #remove weakest individuals from species and stale speces
        self.species.removeWeakPopulation()
        #breed children and fill new population
        self.species.breedChildren(self.innovations)
        # this is the new generation
        self.generation+=1
        # test the new population for fitness
        self.testPopulation()

