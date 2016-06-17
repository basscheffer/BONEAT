from enums import *
import numpy as np


class innovList:

    def __init__(self):

        self.inno_array = np.zeros((0,4),dtype=int)

    def findInnovations(self,innovType,fromNode,toNode,nodeType=0):
        foundlist = list(np.where((self.inno_array[:,0] == innovType) & (self.inno_array[:,1]==fromNode) &
                             (self.inno_array[:,2] == toNode) & (self.inno_array[:,3]==nodeType))[0])
        if foundlist:
            return foundlist
        else:
            return False

    def createNewInnovation(self,innovType,fromNode,toNode,nodeType=0):

        inno_num = len(self.inno_array)

        new_innov = [[innovType,fromNode,toNode,nodeType]]
        self.inno_array = np.concatenate((self.inno_array,new_innov))

        return inno_num

    def getNumberOfInnovations(self):
        return len(self.inno_array)