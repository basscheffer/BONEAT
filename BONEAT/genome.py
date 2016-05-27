from gene import *
from enums import *
import random

class Genome:

    def __init__(self):
        self.l_node_genes = []
        self.l_link_genes = []
        self.fitness = 0.0
        self.performance = {}

    def addNode(self,fromNode,toNode,global_innovations,nodeType=NodeType.HIDDEN,weight=1.0):

        #get all possible innovation numbers for this node
        gil = global_innovations.findInnovations(GeneType.NODE,fromNode,toNode,nodeType)
        if gil:
            l_local_innovation_numbers = self.getNodeNumbers()
            # loop through them
            for gi in gil:
                # if we're already using this one go to the next
                if gi in l_local_innovation_numbers:
                    continue
                # if this one is not in use yet use it
                else:
                    inno_num = gi
                    break
            # if we're using all create a new one
            else:
                inno_num = global_innovations.createNewInnovation(GeneType.NODE,fromNode,toNode,nodeType)
        # if it doesn't exist yet create a new one
        else:
            inno_num = global_innovations.createNewInnovation(GeneType.NODE,fromNode,toNode,nodeType)

        newGene = nodeGene(nodeType,fromNode,toNode,inno_num)
        self.l_node_genes.append(newGene)
        if nodeType == NodeType.HIDDEN:
            self.addLink(fromNode,inno_num,global_innovations,1.0)
            self.addLink(inno_num,toNode,global_innovations,weight)

        return inno_num

    def addLink(self,fromNode,toNode,global_innovations,linkweight=0.0):

        # check if this link is meant to go into an input or bias
        destNode = self.getNode(toNode)
        if destNode:
            if destNode.nodeType == NodeType.INPUT or destNode.nodeType == NodeType.BIAS:
                return False

        # check if this link already exists
        existing_link = self.findLink(fromNode,toNode)
        if existing_link:
            if existing_link.enabled:
                return False
            else:
                existing_link.enabled = True
                return existing_link.innovationNumber

        #if the link doesn't exist yet then make it
        else:
            gil = global_innovations.findInnovations(GeneType.LINK,fromNode,toNode)
            if gil:
                inno_num = gil[0]
            else:
                inno_num = global_innovations.createNewInnovation(GeneType.LINK,fromNode,toNode)

            if linkweight == 0.0:
                weight = random.uniform(-2.0,2.0)
            else:
                weight = linkweight

            newGene = linkGene(fromNode,toNode,weight,inno_num)
            self.l_link_genes.append(newGene)
            return inno_num

    def findLink(self,fromNode,toNode):

        for gene in self.l_link_genes:
            if gene.fromNode == fromNode and gene.toNode == toNode:
                return gene
        else:
            return False

    def getNode(self,nodeNumber):
        for gene in self.l_node_genes:
            if gene.innovationNumber == nodeNumber:
                return gene
        else:
            return False

    def getMaxInnovNum(self):
        all = self.getAllGenes()
        return max(g.innovationNumber for g in all)

    def getAllGenes(self):
        allGenes=[]
        allGenes.extend(self.l_link_genes)
        allGenes.extend(self.l_node_genes)
        return allGenes

    def getNodeNumbers(self):
        return list(g.innovationNumber for g in self.l_node_genes)

    def createFromGeneList(self,gene_list,innovations):
        for g  in gene_list:
            I = innovations.getInnovationByNumber(g.innovationNumber)
            if I.innovType == GeneType.NODE:
                self.l_node_genes.append(g)
            else:
                self.l_link_genes.append(g)

    def mutate(self,global_innovations):
        #CONSTANT
        mut_conn_c = 0.8
        mut_link_c = 0.8
        mut_node_c = 0.5
        perturb_c = 0.9
        switch_c = 0.1
        mut_step = 0.2


        # mutate existing genes
        if random.random() <= mut_conn_c:
            self.geneMutation(perturb_c,switch_c,mut_step)

        # new link
        while True:
            r = random.random()
            if r <= mut_link_c:
                mut_link_c-=r
                self.linkMutation(global_innovations)
            else:
                break

        # new node
        while True:
            r = random.random()
            if r <= mut_node_c:
                mut_link_c-=r
                self.nodeMutation(global_innovations)
            else:
                break

    def geneMutation(self,perturb_c,switch_c,mut_step):
        for gene in self.l_link_genes:
            if random.random() <= perturb_c:
                gene.weight += random.uniform(-mut_step,mut_step)
            else:
                gene.weight = random.uniform(-2.0,2.0)
            if random.random() <= switch_c:
                gene.enabled = not gene.enabled

    def linkMutation(self,glob_innov):

        max_tries = len(self.l_node_genes)
        nodes = self.getNodeNumbers()

        for t in range(max_tries):
            n1 = random.choice(nodes)
            n2 = random.choice(nodes)
            if self.addLink(n1,n2,glob_innov):
                break

    def nodeMutation(self,glob_innov):

        link = random.choice(self.l_link_genes)
        self.addNode(link.fromNode,link.toNode,glob_innov,weight=link.weight)
        link.enabled = False

    def printGenome(self, comment=''):

        print "{} - Genome: {}\n\tperformance:".format(comment,id(self))
        for att in self.performance:
            print "\t\t{} : {}".format(att,self.performance[att])
        print"\tlinks"
        for lg in self.l_link_genes:
            print"\t\tlink {} {}".format(id(lg),vars(lg))
        for ng in self.l_node_genes:
            print"\t\tnode {} {}".format(id(ng),vars(ng))
        print "-----------------------------------//--------------------------------------"

def newSimpleGenome(inputs,outputs,pool):

    gI = pool.innovations

    # make a new genome
    nG = Genome()

    # make the bias node
    nG.addNode(0,0,gI,NodeType.BIAS)

    # make the input nodes
    iNl = []
    for i in range(inputs):
        n = nG.addNode(i+1,0,gI,NodeType.INPUT)
        iNl.append(n)

    # make the output nodes
    oNl = []
    for i in range(outputs):
        n = nG.addNode(0,i+1,gI,NodeType.OUTPUT)
        oNl.append(n)

    # make the links between all these nodes
    # for each output node
    for o in oNl:
        # connect the bias node
        nG.addLink(0,o,gI)
        # and all the inputs
        for i in iNl:
            nG.addLink(i,o,gI)

    return nG

def crossover(genome_pair,innovations):

    equal_fitness = False
    if genome_pair[0].fitness == genome_pair[1].fitness:
        genome1 = genome_pair[0]
        genome2 = genome_pair[1]
        equal_fitness = True
    else:
        genome_pair.sort(key=lambda g: g.fitness, reverse=True)
        genome1 = genome_pair[0]
        genome2 = genome_pair[1]

    genlength = max([genome1.getMaxInnovNum(),genome2.getMaxInnovNum()])+1
    l_gen1 = [None]*genlength
    l_gen2 = [None]*genlength

    G1_genes = genome1.getAllGenes()
    G2_genes = genome1.getAllGenes()

    ####### AAARRRRRGGGHHHHHH this cost me a day,
    # learn: never say = always copy in a new object python will keep reference
    for g in G1_genes:
        l_gen1[g.innovationNumber] = copyGene(g) # ok half day each
    for g in G2_genes:
        l_gen1[g.innovationNumber] = copyGene(g) # ok half day each

    new_genes = []
    for In in range(genlength):
        if l_gen1[In] == None and l_gen2[In] == None:
            continue
        elif l_gen1[In] != None and l_gen2[In] != None:
            if bool(random.getrandbits(1)):
                new_genes.append(l_gen1[In])
            else:
                new_genes.append(l_gen2[In])
        elif l_gen1[In] != None:
            new_genes.append(l_gen1[In])
        elif l_gen2[In] != None and equal_fitness:
            new_genes.append(l_gen1[In])

    NG = Genome()
    NG.createFromGeneList(new_genes,innovations)

    return NG

def copyGenome(genome):
    nG = Genome()
    nG.l_link_genes = []
    for g in genome.l_link_genes:
        nG.l_link_genes.append(copyGene(g))
    for g in genome.l_node_genes:
        nG.l_node_genes.append(copyGene(g))
    return nG








