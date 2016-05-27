import random

class linkGene:

    def __init__(self,inputNode,outputNode,weight=1.0,innovationNumber=0):
        self.innovationNumber = innovationNumber
        self.fromNode = inputNode
        self.toNode = outputNode
        self.weight = weight
        self.enabled = True

class nodeGene:

    def __init__(self,nodeType,inputNode=0,outputNode=0,innovationNumber=0):

        self.innovationNumber = innovationNumber
        self.fromNode = inputNode
        self.toNode = outputNode
        self.nodeType = nodeType

def copyGene(gene):
    if hasattr(gene,'nodeType'):
        ng = nodeGene(gene.nodeType,gene.fromNode,gene.toNode,gene.innovationNumber)
    elif hasattr(gene, 'weight'):
        ng = linkGene(gene.fromNode,gene.toNode,gene.weight,gene.innovationNumber)
        ng.enabled = gene.enabled
    else:
        raise Exception('gene type not recognised')
    return ng