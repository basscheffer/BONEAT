from enums import *
import numpy as np


class innovList:

    def __init__(self):
        self.l_innovations = []
        self.new_innov_number = 0

    def findInnovations(self,innovType,fromNode,toNode,nodeType=None):

        foundlist = []

        for i in self.l_innovations:
            if innovType == i.innovType and nodeType == i.nodeType\
                and fromNode == i.fromNode and toNode == i.toNode:
                foundlist.append(i.innovNumber)

        if foundlist:
            return foundlist
        else:
            return False

    def makeArray(self):
        self.inno_array = np.zeros((len(self.l_innovations),4),dtype=int)
        for idx, inn in enumerate(self.l_innovations):
            if inn.nodeType:
                nt = inn.nodeType
            else:
                nt = 0
            self.inno_array[idx] = [inn.innovType,inn.fromNode,inn.toNode,nt]

    def findInnovationsN(self,innovType,fromNode,toNode,nodeType=0):
        print self.inno_array
        foundlist = list(np.where((self.inno_array[:,0] == innovType) & (self.inno_array[:,1]==fromNode) &
                             (self.inno_array[:,2] == toNode) & (self.inno_array[:,3]==nodeType))[0])
        print foundlist
        if foundlist:
            return foundlist
        else:
            print "returned false"
            return False

    def createNewInnovation(self,innovType,fromNode,toNode,nodeType=None):

        inno_num = self.new_innov_number
        new_innov = innovation(inno_num,innovType,nodeType,fromNode,toNode)
        self.new_innov_number += 1
        self.l_innovations.append(new_innov)
        return inno_num

    def getInnovationByNumber(self,number):
        # for i in self.l_innovations:
        #     if i.innovNumber == number:
        #         return i
        # else:
        #     return False
        inno = self.l_innovations[number]
        if inno.innovNumber == number:
            return inno
        else:
            return False


class innovation:

    def __init__(self,innovNumber,innovType,nodeType,fromNode,toNode):

        self.innovNumber = innovNumber
        self.innovType = innovType
        self.nodeType = nodeType
        self.fromNode = fromNode
        self.toNode = toNode