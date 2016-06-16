from PyQt4.QtGui import *
from PyQt4.QtCore import *
from enums import *
import sys
import math

def inArray(num,array):
    for l in array:
        if num in l:
            return True
    else:
        return False

def sigmoid(x):
  return 1 / (1 + math.exp(-x))



class graphicNode:

    def __init__(self,y_pos,x_pos,type,number):
        self.y_pos = y_pos
        self.x_pos = x_pos
        self.type = type
        self.number = number

class graphicLink:

    def __init__(self,x1,y1,x2,y2,weight):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.weight = weight

class neuralNetVisualiser(QGraphicsScene):

    def __init__(self,width,height):
        QGraphicsScene.__init__(self,QRectF(0,0,width,height))
        self.border = 3
        self.adjH = height-(2*self.border)
        self.adjW = width-(2*self.border)
        bbr = QBrush(Qt.black)
        self.setBackgroundBrush(bbr)

    def readGTstring(self,GTstring):
        GTGstring = GTstring.split(">NEUR")[1]
        GTNstring = GTGstring.split(">LINK")[0]
        GTLstring = GTGstring.split(">LINK")[1]
        rowlist = GTLstring.split()
        self.linklist = []
        for row in rowlist:
            sp = row.split(";")
            l = [int(sp[0]),int(sp[1]),float(sp[2])]
            self.linklist.append(l)
        self.max_weight = max(abs(l[2]) for l in self.linklist)

        rowlist = GTNstring.split()
        self.neurlist = []
        for row in rowlist:
            sp = row.split(";")
            l = [int(sp[0]),int(sp[1]),int(sp[2])]
            self.neurlist.append(l)
        
        self.layerarray = []
        inlist = []
        outlist = []
        for n in self.neurlist:
            if n[1] == NodeType.INPUT or n[1] == NodeType.BIAS:
                inlist.append(n[0])
            if n[1] == NodeType.OUTPUT:
                outlist.append(n[0])
        self.layerarray.append(outlist)
        self.layerarray.append(inlist)
        
        allcreated = False
        while not allcreated:
            allcreated = True
            newlayerlist = []
            for l in self.linklist:
                if l[0] in newlayerlist or inArray(l[0],self.layerarray):
                    pass
                else:
                    if inArray(l[1],self.layerarray[:-1]):
                        newlayerlist.append(l[0])
                    else:
                        allcreated = False
            newlayerlist.sort(reverse=False)
            if newlayerlist:
                self.layerarray.insert(len(self.layerarray)-1,newlayerlist)
        for layer in self.layerarray:
            print layer
    
    def makeGraphicNodes(self):
        self.NP_list = []
        y_delta = 1.0/(len(self.layerarray)-1.0)
        for y , layer in enumerate(self.layerarray):
            x_delta = 1.0/len(layer)
            for x , node in enumerate(layer):
                t = self.getNodeType(node)
                yp = y*y_delta
                xp = (x*x_delta)+(x_delta/2)
                gN = graphicNode(yp,xp,t,node)
                self.NP_list.append(gN)

    def makeGraphicLinks(self):
        self.LP_list = []
        for link in self.linklist:
            x1,y1 = self.getNodePosition(link[0])
            x2,y2 = self.getNodePosition(link[1])
            w = link[2]/self.max_weight
            nL = graphicLink(x1,y1,x2,y2,w)
            self.LP_list.append(nL)

    def drawLinks(self):
        for LP in self.LP_list:
            pen = QPen()
            w = abs(LP.weight)*10.0
            pen.setWidthF(w)
            if LP.weight < 0.0:
                pen.setColor(Qt.red)
            else:
                pen.setColor(Qt.green)
            x1 = LP.x1*self.adjW+self.border
            y1 = LP.y1*self.adjH+self.border
            x2 = LP.x2*self.adjW+self.border
            y2 = LP.y2*self.adjH+self.border
            self.addLine(x1,y1,x2,y2,pen = pen)

    def drawNodes(self):
        for NP in self.NP_list:
            brush = QBrush(Qt.SolidPattern)
            if NP.type == NodeType.BIAS:
                brush.setColor(Qt.green)
            elif NP.type == NodeType.INPUT:
                brush.setColor(Qt.red)
            elif NP.type == NodeType.OUTPUT:
                brush.setColor(Qt.blue)
            else:
                brush.setColor(Qt.magenta)
            x = (NP.x_pos*self.adjW+self.border)-15
            y = (NP.y_pos*self.adjH+self.border)-15
            self.addEllipse(x,y,30,30,brush = brush)

            font = QFont()
            font.setPointSize(10)
            font.setBold(True)
            T = self.addText(str(NP.number),font=font)
            T.setPos(x,y+30)
            T.setDefaultTextColor(Qt.white)

    def getNodePosition(self,node):
        for n in self.NP_list:
            if n.number == node:
                return n.x_pos, n.y_pos

    def getNodeType(self,number):
        for n in self.neurlist:
            if n[0] == number:
                return n[1]

    def drawArc(self):
        p = QPen(Qt.white)
        PP = QPainterPath()
        PP.moveTo(200,50)
        PP.arcTo(0,0,200,100,0,-180)
        self.addPath(PP,pen=p)

class W(QGraphicsView):

    def __init__(self):
        QGraphicsView.__init__(self)
        self.resize(1000,700)

        NNV = neuralNetVisualiser(900,600)
        # NNV.drawArc()
        GTS = open("testchild.txt").read()
        NNV.readGTstring(GTS)
        NNV.makeGraphicNodes()
        NNV.makeGraphicLinks()
        NNV.drawLinks()
        NNV.drawNodes()

        self.setScene(NNV)

def main():
    app = QApplication(sys.argv)
    window = W()
    window.show()
    sys.exit(app.exec_())

if __name__==("__main__"):
    main()