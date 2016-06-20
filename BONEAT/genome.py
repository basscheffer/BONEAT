from gene import *
from enums import *
import random
import copy

class Genome:

    def __init__(self,settings):
        self.settings = settings

        self.l_node_genes = []
        self.l_link_genes = []
        self.fitness = 0.0
        self.performance = {}

        self.species_id = 0

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
                w = float(self.settings["weight"])
                weight = random.uniform(-w,w)
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
        return max(self.getAllGenesDict().keys())

    def getAllGenesDict(self):
        allGenes={}
        for lg in self.l_link_genes:
            allGenes[lg.innovationNumber] = lg
        for ng in self.l_node_genes:
            allGenes[ng.innovationNumber] = ng
        return allGenes

    def getNodeNumbers(self):
        return list(g.innovationNumber for g in self.l_node_genes)

    def createFromGeneList(self,gene_list):
        for g in gene_list:
            if hasattr(g,'nodeType'):
                self.l_node_genes.append(g)
            elif hasattr(g, 'weight'):
                self.l_link_genes.append(g)
            else:
                raise Exception('gene type not recognised')

    def mutate(self,global_innovations):

        mut_conn_c = float(self.settings["mutation"])
        mut_link_c = float(self.settings["new_link"])
        mut_node_c = float(self.settings["new_node"])
        perturb_c = float(self.settings["perturbing"])
        mut_step = float(self.settings["step"])

        # mutate existing genes

        self.geneMutation(mut_conn_c,perturb_c,mut_step)

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
                mut_node_c-=r
                self.nodeMutation(global_innovations)
            else:
                break

    def geneMutation(self,mut_c,perturb_c,mut_step):
        for gene in self.l_link_genes:
            if random.random() <= mut_c:
                if random.random() <= perturb_c:
                    gene.weight += random.uniform(-mut_step,mut_step)
                else:
                    w = float(self.settings["weight"])
                    gene.weight = random.uniform(-w,w)
                # if random.random() <= switch_c:
                #     gene.enabled = not gene.enabled

    def linkMutation(self,glob_innov):

        max_tries = len(self.l_node_genes)
        nodes = self.getNodeNumbers()

        if random.random() <= float(self.settings["recur_boost"]):
            for t in range(max_tries):
                n = random.choice(nodes)
                if self.addLink(n,n,glob_innov):
                    break
        else:
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

    def makeGenotypeString(self):

        ## properties ##
        pair = self.settings["pair"]
        tf = self.settings["timeframe"]
        vers = 0.0
        ## normalise constants ##
        np = "data/norm_fs/{}{}_NormConst.txt"\
            .format(pair,tf)
        with open(np,"r") as f:
            normstr = "\n"+f.read().rstrip()
        ## neurons ##
        neurstr = ""
        for n in self.l_node_genes:
            nm = n.innovationNumber
            tp = n.nodeType
            io = 0
            if tp == NodeType.INPUT:
                io = n.fromNode
            if tp == NodeType.OUTPUT:
                io = n.toNode

            s = "\n{};{};{}".format(nm,tp,io)
            neurstr+=s
        ## links ##
        linkstr = ""
        for l in self.l_link_genes:
            if l.enabled:
                s = "\n{};{};{}".format(l.fromNode,l.toNode,l.weight)
                linkstr+=s

        retstr = """>PROP
PAIR;{}
TF;{}
VERS;{}
>PREP{}
>NEUR{}
>LINK{}
""".format(pair,tf,vers,normstr,neurstr,linkstr)
        return retstr

def newSimpleGenome(inputs,outputs,pool,settings):

    gI = pool.innovations

    # make a new genome
    nG = Genome(settings)

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

def crossover(genome_pair,settings):

    if genome_pair[1].fitness > genome_pair[0].fitness:
        G1 = genome_pair[1]
        G2 = genome_pair[0]
    else:
        G1 = genome_pair[0]
        G2 = genome_pair[1]

    G1_genes = G1.getAllGenesDict()
    G2_genes = G2.getAllGenesDict()

    new_genes = []
    for key, gene in G1_genes.iteritems():
        if key in G2_genes and bool(random.getrandbits(1)):
            new_genes.append(copy.copy(G2_genes[key]))
        else:
            new_genes.append(copy.copy(gene))

    ####### AAARRRRRGGGHHHHHH this cost me a day,
    # learn: never say = always copy in a new object python will keep reference

    NG = Genome(settings)

    NG.createFromGeneList(new_genes)

    return NG

def copyGenome(genome,settings):
    nG = Genome(settings)
    nG.l_link_genes = []
    for g in genome.l_link_genes:
        nG.l_link_genes.append(copyGene(g))
    for g in genome.l_node_genes:
        nG.l_node_genes.append(copyGene(g))
    return nG

def buildFromGTFile(genotype_file):
    nodelist = []
    linklist = []

    with open(genotype_file,"r") as gtf:
        gts = gtf.read()
        ns,ls = gts.split(">NEUR")[1].split(">LINK")
        nsl =  ns.split()
        lsl = ls.split()

        for ni in nsl:
            x = ni.split(";")
            nodelist.append([int(x[0]),int(x[1]),int(x[2])])
        for li in lsl:
            x = li.split(";")
            linklist.append([int(x[0]),int(x[1]),float(x[2])])

    settings = {"pair":"AUDUSD","timeframe":240}
    NG = Genome(settings)
    for node in nodelist:
        type = node[1]
        fromnode = 0
        tonode = 0
        innonum = node[0]
        if type == NodeType.INPUT:
            fromnode = node[2]
        elif type == NodeType.OUTPUT:
            tonode = node[2]
        Ng = nodeGene(type,fromnode,tonode,innonum)
        NG.l_node_genes.append(Ng)
    for link in linklist:
        fromnode = link[0]
        tonode = link[1]
        weight = link[2]
        Nl = linkGene(fromnode,tonode,weight,0)
        NG.l_link_genes.append(Nl)

    return NG




