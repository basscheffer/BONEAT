from enums import *


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

    def createNewInnovation(self,innovType,fromNode,toNode,nodeType=None):

        inno_num = self.new_innov_number
        new_innov = innovation(inno_num,innovType,nodeType,fromNode,toNode)
        self.new_innov_number += 1
        self.l_innovations.append(new_innov)
        return inno_num

    def getInnovationByNumber(self,number):
        for i in self.l_innovations:
            if i.innovNumber == number:
                return i
        else:
            return False


class innovation:

    def __init__(self,innovNumber,innovType,nodeType,fromNode,toNode):

        self.innovNumber = innovNumber
        self.innovType = innovType
        self.nodeType = nodeType
        self.fromNode = fromNode
        self.toNode = toNode