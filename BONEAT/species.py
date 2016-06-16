import math
import random
import genome
import time
from timeit import default_timer as timer

class SpeciesList:

    def __init__(self,settings):

        self.settings = settings

        self.disjointC = float(settings["d_factor"])
        self.excessC = float(settings["e_factor"])
        self.weightsC = float(settings["w_factor"])
        self.threshold = float(settings["threshold"])
        self.population = int(settings["population"])

        self.breedtime = 0.0
        self.mutatetime =0.0

        self.max_pop_fitness = 0.0

        self.l_species = []
        self.next_id = 1

    def addToSpecies(self,genome):

        # loop through all species and check to which it belongs
        for s in self.l_species:
            if self.sameSpecies(s.root_genome,genome):
                s.l_genomes.append(genome)
                break

        # if it didn't belong to any make a new one
        else:
            s = species(self.next_id,genome,self.settings)
            self.next_id += 1
            self.l_species.append(s)

    def sameSpecies(self,speciesGenome,newGenome):

        # get genome difference
        D,W = difference(speciesGenome,newGenome)

        # calculate delta
        delta = self.disjointC*D+self.weightsC*W

        # check if this is within threshold
        return delta <= self.threshold

    def getAllGenomes(self):
        agl = []
        for s in self.l_species:
            agl.extend(s.l_genomes)
        return agl

    def removeWeakPopulation(self):

        self.max_pop_fitness = self.getMaxFitness()
        surv = []

        for species in self.l_species:
            # remove stale species
            if species.checkStaleness(self.max_pop_fitness):
                continue
            # remove weak population
            else:
                species.removeWeak()
                surv.append(species)

        allAlive = False
        while not allAlive:
            allAlive = True

            new_s_list = []
            sum_avg_fitness = sum(s.avg_fitness for s in self.l_species)

            for species in surv:
                if sum_avg_fitness != 0.0:
                    breed = int(math.floor((species.avg_fitness/sum_avg_fitness)*self.population))
                else:
                    breed = int(math.floor(float(self.population)/len(self.l_species)))

                if breed <= 0:
                    allAlive = False
                    continue
                else:
                    species.breed = breed
                    new_s_list.append(species)

            surv = new_s_list

        self.l_species = surv

    def getMaxFitness(self):
        return max(s.max_fitness for s in self.l_species)

    def breedChildren(self,innovations):

        self.breedtime = 0.0
        self.mutatetime = 0.0

        crossoverchance = float(self.settings["crossover"])

        new_gen_children = []
        # breed all the children for each species
        for s in self.l_species:
            new_gen_children.extend(s.breedChildren(innovations))
            self.breedtime += s.breedtime
            self.mutatetime += s.mutatetime

        # fill the remainder with wild children
        remainder = self.population-len(new_gen_children)
        all_Gs = self.getAllGenomes()
        for i in range(remainder):
            bt0 = timer()
            if random.random() <= crossoverchance and len(all_Gs)>1:
                child=genome.crossover(random.sample(all_Gs,2),innovations,self.settings)
            else:
                child = genome.copyGenome(random.choice(all_Gs),self.settings)
            bt1 = timer()
            self.breedtime += (bt1-bt0)
            child.mutate(innovations)
            bt2 = timer()
            self.mutatetime += (bt2-bt1)
            new_gen_children.append(child)

        self.newGeneration(new_gen_children)

    def newGeneration(self,new_generation):
        self.killOldGeneration()
        self.loadNewGenertion(new_generation)
        self.killExtinctSpecies()

    def killExtinctSpecies(self):
        surv = []
        for s in self.l_species:
            if len(s.l_genomes) > 0:
                surv.append(s)
        self.l_species = surv

    def loadNewGenertion(self,new_population):
        for G in new_population:
            self.addToSpecies(G)

    def killOldGeneration(self):
        for s in self.l_species:
            s.l_genomes = []

    def getGenerationData(self):
        newdata = []
        for species in self.l_species:
            speciesData = species.getSpeciesData()
            newdata.append(speciesData)
        return newdata

class species:

    def __init__(self,species_id,genome,settings):
        self.sp_id = species_id
        self.settings = settings
        self.root_genome = genome
        self.l_genomes = [genome]
        self.staleness = 0
        self.avg_fitness = 0.0
        self.max_fitness = 0.0
        self.breed = 0

        self.breedtime = 0.0
        self.mutatetime = 0.0

    def getSpeciesData(self):

        s_num = self.sp_id
        s_pop = len(self.l_genomes)
        s_topfit = self.getMaxFitness()
        self.calculateAverageFitness()
        s_avg_fit = self.avg_fitness
        self.l_genomes.sort(key=lambda g: g.fitness, reverse=True)
        s_topf_perf = self.l_genomes[0].performance

        sdata = [s_num,s_pop,s_topfit,s_avg_fit,s_topf_perf]
        return sdata

    def removeWeak(self):
        split = int(math.ceil(len(self.l_genomes)/2.0))
        self.l_genomes.sort(key=lambda g: g.fitness, reverse=True)
        surv =self.l_genomes[:split]
        self.l_genomes = surv
        self.calculateAverageFitness()

    def checkStaleness(self,max_pop_fitness):
        # get the new max fitness
        maxperf = self.getMaxFitness()
        # if it was more than previous max update it and reset staleness
        if maxperf > self.max_fitness:
            self.max_fitness = maxperf
            self.staleness = 0
        # else increase staleness
        else:
            self.staleness += 1

        # if it is stale for 20 generations and is not the best performing species it's stale
        if self.staleness > int(self.settings["staleness"]) and self.max_fitness < max_pop_fitness:
            return True
        else:
            return False

    def getMaxFitness(self):
        return max(g.fitness for g in self.l_genomes)

    def calculateAverageFitness(self):
        self.avg_fitness = sum(g.fitness for g in self.l_genomes)/float(len(self.l_genomes))

    def breedChildren(self,innovations):

        self.breedtime = 0.0
        self.mutatetime = 0.0

        crossoverchance = float(self.settings["crossover"])

        # update root genome
        self.root_genome = random.choice(self.l_genomes)

        children = []

        # copy genome 0
        # children.append(self.l_genomes[0])

        # loop through breed
        for i in range(self.breed):
            bt0  = timer()
            if random.random() <= crossoverchance and len(self.l_genomes)>1:
                child=genome.crossover(random.sample(self.l_genomes,2),innovations,self.settings)
            else:
                child = genome.copyGenome(random.choice(self.l_genomes),self.settings)
            bt1  = timer()
            self.breedtime +=  (bt1-bt0)
            child.mutate(innovations)
            bt2  = timer()
            self.mutatetime += (bt2-bt1)

            children.append(child)

        return children

def difference(genome1,genome2):

    disjointcounter = 0.0
    weightsum = 0.0
    weightcounter = 0.0
    max_genes = max(len(genome1.l_link_genes),len(genome2.l_link_genes))
    max_innov = max(genome1.getMaxInnovNum(),genome2.getMaxInnovNum())

    il1 = [None]*(max_innov+1)
    il2 = [None]*(max_innov+1)

    for g in genome1.l_link_genes:
        il1[g.innovationNumber]=g.weight

    for g in genome2.l_link_genes:
        il2[g.innovationNumber]=g.weight

    for i in range(len(il1)):
        if il1[i] != il2[i]:
            if il1[i] == None or il2[i] == None:
                disjointcounter += 1.0
            if il1[i] != None and il2[i] != None:
                weightcounter += 1.0
                weightsum += abs(il1[i]-il2[i])

    djr = disjointcounter/max_genes
    if weightcounter > 0.0:
        aw = weightsum/weightcounter
    else:
        aw = 0.0

    return djr, aw


