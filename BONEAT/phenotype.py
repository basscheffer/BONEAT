from enums import *
import math
import yappi

class Neuron:

    def __init__(self,neuronType,i_o_index = 0):
        self.Ntype = neuronType
        self.io = i_o_index
        self.links = []
        self.inputSum = 0.0
        self.output = 0.0

class Link:

    def __init__(self,fromNode,weight):
        self.fromNeuron = fromNode
        self.weight = weight

class neuralNetwork:

    def __init__(self, genome):
        self.genome = genome
        self.inputs = []
        self.neurons = {}
        self.outputs= []

        self.buildNetwork()

    def buildNetwork(self):

        # first build all the neurons
        for node in self.genome.l_node_genes:
            # if in or output set i/o of neuron
            io=0
            if node.nodeType == NodeType.INPUT:
                io = node.fromNode
            if node.nodeType == NodeType.OUTPUT:
                io = node.toNode
                self.outputs.append(0.0)
            # make new neuron
            newNeuron = Neuron(node.nodeType,io)
            # add to neuron list at innovation number index
            self.neurons[node.innovationNumber]=newNeuron

        # then add all the links
        for link in self.genome.l_link_genes:
            if link.enabled:
                # make a new link
                newLink = Link(link.fromNode,link.weight)
                # and add to the neuron
                self.neurons[link.toNode].links.append(newLink)

    def update(self,inputList):

        self.inputs = inputList

        # set the input and bias values
        for i,N in self.neurons.iteritems():
            if N.Ntype == NodeType.INPUT:
                N.output = self.inputs[N.io-1]
            if N.Ntype == NodeType.BIAS:
                N.output = 1.0

        # calculate all the input-sums
        for i,N in self.neurons.iteritems():
            N.inputSum = 0.0
            for l in N.links:
                v = self.neurons[l.fromNeuron].output
                w = l.weight
                s = v*w
                N.inputSum += s

        # calculate all the activations
        for i,N in self.neurons.iteritems():
            N.output = math.tanh(N.inputSum)

        # add result to output list
            if N.Ntype == NodeType.OUTPUT:
                self.outputs[N.io-1]=N.output

        # fs = yappi.get_func_stats()
        # fs.sort("tsub")
        # fs.print_all( columns={0:("name",100), 1:("ncall", 5), 2:("tsub", 8), 3:("ttot", 8), 4:("tavg",8)})


        return self.outputs







