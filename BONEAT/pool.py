import ConfigParser
import csv
from timeit import default_timer as timer

import simulate as sim
from genome import *
from innovation import *
from species import *
import db_log


class Pool:

    def __init__(self,cfg_filepath):

        self.getSettingsFromCfg(cfg_filepath)

        self.population = int(self.GS["population"])
        self.species = SpeciesList(self.GS)
        self.innovations = innovList()
        self.generation = 0
        self.processors = int(self.GS["cores"])

        self.tottime = 0.0
        self.testtime = 0.0
        self.culltime = 0.0
        self.newgentime = 0.0
        self.breedtime = 0.0
        self.mutatetime = 0.0

        self.timerdatafile="data/timerfile/{}{}_td.csv".format(self.GS["pair"],self.GS["timeframe"])
        with open(self.timerdatafile,"w") as tdf:
            writer = csv.writer(tdf, delimiter=',',quotechar='"')
            writer.writerow(("generation","total","test","remove weak","breed","cross/copy","mutate"))

        csvpath="data/ga_logs/{}{}.csv".format(self.GS["pair"],self.GS["timeframe"])
        with open(csvpath,"w") as csvf:
            writer = csv.writer(csvf, delimiter=',',quotechar='"')
            writer.writerow(("generation","species","population","max fitness","avg fitness","best performance"))

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
              %(self.generation,len(self.species.l_species),self.innovations.getNumberOfInnovations())
        sim.fastSimulateConfirm(self.species.getAllGenomes(),self.GS)

    def logGenerationResults(self):
        data = self.species.getGenerationData()
        csvpath="data/ga_logs/{}{}.csv".format(self.GS["pair"],self.GS["timeframe"])
        with open(csvpath,"a") as csvf:
            writer = csv.writer(csvf, delimiter=',',quotechar='"')
            for row in data:
                line = [self.generation]
                line.extend(row)
                writer.writerow(line)

    def logGenoTypes(self):
        DBL = db_log.GTLogger()
        AGL = self.species.getAllGenomes()
        AGL.sort(key=lambda g: g.fitness, reverse=True)
        cull = int(math.ceil(len(AGL)/10.0))
        for i in range(cull):
            D = {"pair":self.GS["pair"],
                 "generation":self.generation,
                 "species":AGL[i].species_id,
                 "confirmfactor":0.0
                 }
            D.update(AGL[i].performance)
            DBL.logGenoType(D,AGL[i].makeGenotypeString(),cull)
        DBL.cullGenoTypeLog(cull)
        DBL.close()

    def logTimer(self):
        data = [self.generation,self.tottime,self.testtime,self.culltime,self.newgentime,self.breedtime,self.mutatetime]
        with open(self.timerdatafile,"a") as csvf:
            writer = csv.writer(csvf, delimiter=',',quotechar='"')
            writer.writerow(data)

    def evolvePopulation(self):

        t0 = timer()
        if self.generation == 0:
            #start a new population
            self.newPopulation()
            t2 = timer()
            self.newgentime = (t2-t0)
            self.breedtime = (t2-t0)
        else:
            #remove weakest individuals from species and stale speces
            self.species.removeWeakPopulation()
            t1 = timer()
            self.culltime = (t1-t0)

            #breed children and fill new population
            self.species.breedChildren(self.innovations)

            t2 = timer()
            self.newgentime = (t2-t1)
            self.breedtime = self.species.breedtime
            self.mutatetime = self.species.mutatetime

        # this is the new generation
        self.generation+=1

        # test the new population for fitness
        self.testPopulation()
        t3 = timer()
        self.testtime = (t3-t2)
        self.logGenerationResults()
        self.logGenoTypes()

        self.tottime = (t3-t0)

        self.logTimer()


