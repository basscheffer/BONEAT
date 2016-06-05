from PyQt4.QtGui import *
from PyQt4.QtCore import *
from datetime import *
from signals import *
import ConfigParser
import sys
import os

class mainWindow(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.initGUI()

    def initGUI(self):
        self.settingsWidget()
        self.monitoringWidget()

        self.mainTabC = QTabWidget()
        self.mainTabC.addTab(self.settW,"Settings")
        self.mainTabC.addTab(self.monW,"Monitor")
        self.setCentralWidget(self.mainTabC)

    def saveConfigFile(self):
        config = ConfigParser.RawConfigParser()

        self.getSettingsDict()

        for section in self.settingsdict:
            config.add_section(section)
            for setting in self.settingsdict[section]:
                val = self.settingsdict[section][setting]
                config.set(section,setting,val)

        with open(self.simSettGb.filepath, 'w') as configfile:
            config.write(configfile)

    def loadConfigFile(self):
        config = ConfigParser.RawConfigParser()
        config.read(str(self.simSettGb.filepath))

        self.settingsdict={}
        sections = config.sections()
        for sec in sections:
            d = {sec:dict(config.items(sec))}
            self.settingsdict.update(d)
        self.setSettings()

    def setSettings(self):
        for i in range(4):
            sW = self.settlay.itemAt(i).widget()
            sect = sW.sectCode
            sW.setSettings(self.settingsdict[sect])

    def getSettingsDict(self):
        self.settingsdict = {}
        for i in range(4):
            sW = self.settlay.itemAt(i).widget()
            sect = sW.sectCode
            resdict = sW.getSettings()
            self.settingsdict[sect] = resdict

    def settingsWidget(self):
        self.settW = QWidget()
        self.settlay = QGridLayout()
        self.settW.setLayout(self.settlay)

        self.simSettGb = simulationSettings("simulation","Simulation settings")
        self.simSettGb.addSlider("spread","Spread",5.0,0.0,1.5,0.1)
        self.simSettGb.addDropDown("perf_mode","Performance function",["profit","t*p2/d","profit/drawdown","profit^2/drawdown"])
        self.simSettGb.addSlider("cores","CPU Cores",12,1,4,1)
        self.simSettGb.addSlider("population","Population",2000,30,300,10)
        self.simSettGb.addButtons()
        self.simSettGb.signals.saveconfig.connect(self.saveConfigFile)
        self.simSettGb.signals.loadconfig.connect(self.loadConfigFile)

        self.dataSettGb = dataSettings("data","Data settings")
        self.dataSettGb.signals.basename.connect(self.simSettGb.setFilepath)
        self.dataSettGb.requestSignal()

        self.specSettGb = settingsBox("speciation","Speciation settings")
        self.specSettGb.addSlider("threshold","Speciation threshold",5.0,0.2,1.0,0.1)
        self.specSettGb.addSlider("d_factor","Disjoint weight",3.0,0.0,1.0,0.1)
        self.specSettGb.addSlider("e_factor","Excess weight",3.0,0.0,1.0,0.1)
        self.specSettGb.addSlider("w_factor","Weight difference weight",3.0,0.0,1.0,0.1)
        self.specSettGb.addSlider("staleness","Stale species",30,1,15,1)

        self.mutSettGb = settingsBox("mutation","Mutation settings")
        self.mutSettGb.addSlider("crossover","Crossover chance",1.0,0.0,0.8,0.05)
        self.mutSettGb.addSlider("mutation","Existing link mutation chance",1.0,0.0,0.8,0.05)
        self.mutSettGb.addSlider("perturbing","Weight perturbing chance",1.0,0.0,0.8,0.05)
        # self.mutSettGb.addSlider("switch","Weight enable mutation chance",0.5,0.0,0.1,0.05)
        self.mutSettGb.addSlider("step","Weight perturbing step-size",10.0,0.2,2.0,0.2)
        self.mutSettGb.addSlider("weight","New weight range",10.0,1.0,2.0,0.5)
        self.mutSettGb.addSlider("new_link","New link mutation chance",3.0,0.0,1.0,0.1)
        self.mutSettGb.addSlider("new_node","New node mutation chance",3.0,0.0,1.0,0.1)
        self.mutSettGb.addSlider("recur_boost","Recurrent connection boost",1.0,0.0,0.3,0.05)


        self.settlay.addWidget(self.simSettGb,0,0)
        self.settlay.addWidget(self.dataSettGb,1,0)
        self.settlay.addWidget(self.specSettGb,0,1)
        self.settlay.addWidget(self.mutSettGb,1,1)
        self.setStretch(self.settlay)

    def monitoringWidget(self):
        self.monW = QWidget()
        lay = QGridLayout()
        self.monW.setLayout(lay)

        self.conMonGb = QGroupBox("Simulation")
        self.perfMonGb = QGroupBox("Performance")
        self.specMonGb = QGroupBox("Speciation")
        self.netMonGb = QGroupBox("Network")

        lay.addWidget(self.conMonGb,0,0)
        lay.addWidget(self.specMonGb,1,0)
        lay.addWidget(self.perfMonGb,0,1)
        lay.addWidget(self.netMonGb,1,1)
        self.setStretch(lay)

    def setStretch(self,grid_layout):
        for i in range(grid_layout.columnCount()):
            grid_layout.setColumnStretch(i,1)
        for i in range(grid_layout.rowCount()):
            grid_layout.setRowStretch(i,1)

    def updateFilePath(self):
        bn = self.dataSettGb.getBaseName()
        self.simSettGb.filepath = "data/config_files/{}.cfg".format(bn)

class settingsBox(QGroupBox):

    def __init__(self,sectCode,title):
        QGroupBox.__init__(self,title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.sectCode = sectCode

    def addSlider(self,settCode,name,max_val,min_val,default,step):
        slid = slideAndNum(settCode,name,max_val,min_val,default,step)
        self.layout.addWidget(slid)

    def addDropDown(self,settCode,name,itemlist):
        drop = comboSetting(settCode,name)
        drop.addItems(itemlist)
        self.layout.addWidget(drop)
        return drop

    def addDateRange(self,settCode,name,start_date,end_date):
        date = dateRange(settCode,name,start_date,end_date)
        self.layout.addWidget(date)
        return date

    def getSettings(self):
        settDict = {}
        for i in range(self.layout.count()):
            W = self.layout.itemAt(i).widget()
            try:
                nS = W.getSetting()
                settDict.update(nS)
            except:
                pass
        return settDict

    def setSettings(self,settingsdict):

        for k in settingsdict:
            try:
                W = self.getWidgetBySetCode(k)
                W.setValue({k:settingsdict[k]})
            except:
                pass

    def getWidgetBySetCode(self,SettCode):
        for i in range(self.layout.count()):
            W = self.layout.itemAt(i).widget()
            if W.settCode in SettCode:
                return W

class simulationSettings(settingsBox):

    def __init__(self,sectCode,title):
        settingsBox.__init__(self,sectCode,title)
        self.signals = Signals()
        self.filepath = ""

    def setFilepath(self,new_path):
        self.filepath = "data/config_files/{}.cfg".format(new_path)

    def addButtons(self):
        self.but_layout = QHBoxLayout()
        self.layout.addLayout(self.but_layout)
        self.saveButt = QPushButton("Save as config file")
        self.openButt = QPushButton("open config file")
        self.but_layout.addWidget(self.saveButt)
        self.but_layout.addWidget(self.openButt)
        self.saveButt.clicked.connect(self.saveDialog)
        self.openButt.clicked.connect(self.loadDialog)

    def saveDialog(self):
        fp = QFileDialog.getSaveFileName(self,"Save config file",
                            self.filepath,
                            "Config (*.cfg)")
        if fp:
            self.filepath = fp
            self.signals.saveconfig.emit()

    def loadDialog(self):
        fp = QFileDialog.getOpenFileName(self,"Load config file",
                            self.filepath,
                            "Config (*.cfg)")
        if fp:
            self.filepath = fp
            self.signals.loadconfig.emit()

class dataSettings(settingsBox):

    def __init__(self,sectCode,title):
        settingsBox.__init__(self,sectCode,title)
        self.signals = Signals()
        self.getAvailableData()

        self.pdd = self.addDropDown("pair","Pair",[])
        self.tfdd = self.addDropDown("timeframe","Timeframe",[])
        self.tde = self.addDateRange("traindata","Training data range",date(2000,1,1),date.today())
        self.cde = self.addDateRange("confirmdata","Confirmation data range",date(2000,1,1),date.today())
        self.tstde = self.addDateRange("test_data","Test data range",date(2000,1,1),date.today())

        self.updatePairs()
        self.updateTimeFrames()
        self.updateDates()
        self.pdd.comboB.currentIndexChanged.connect(self.updateTimeFrames)
        self.tfdd.comboB.currentIndexChanged.connect(self.updateDates)

    def requestSignal(self):
        self.signals.basename.emit(self.getBaseName())

    def getBaseName(self):
        tf_dict = {"M5":5,"M15":15,"M30":30,"H1":60,"H4":240,"D1":1440}
        pair = str(self.pdd.comboB.currentText())
        tf = tf_dict[str(self.tfdd.comboB.currentText())]
        return pair+str(tf)

    def updatePairs(self):
        l = self.datadict.keys()
        self.pdd.addItems(l)

    def updateTimeFrames(self):
        pair = str(self.pdd.comboB.currentText())
        l = self.datadict[pair].keys()
        self.tfdd.addItems(l)
        self.updateDates()
        self.signals.basename.emit(self.getBaseName())

    def updateDates(self):
        pair = str(self.pdd.comboB.currentText())
        tf = str(self.tfdd.comboB.currentText())
        self.tde.minDate = self.datadict[pair][tf][0]
        self.tde.maxDate = self.datadict[pair][tf][1]
        self.tde.updateDateInputs()
        self.cde.minDate = self.datadict[pair][tf][0]
        self.cde.maxDate = self.datadict[pair][tf][1]
        self.cde.updateDateInputs()
        self.tstde.minDate = self.datadict[pair][tf][0]
        self.tstde.maxDate = self.datadict[pair][tf][1]
        self.tstde.updateDateInputs()

    def getAvailableData(self):
        tf_dict = {5:"M5",15:"M15",30:"M30",60:"H1",240:"H4",1440:"D1"}
        base_dir = "data/raw_price_data/"
        self.datadict = {}

        for file in os.listdir(base_dir):

            if file.endswith(".csv"):
                name = file.split('.')[0]
                pair = name[:6]
                tf = tf_dict[int(name[6:])]
                tl = [0]*2

                with open(base_dir+file) as fh:
                    ds = fh.readline().split(",")[0]
                    tl[0] = datetime.strptime(ds,"%Y.%m.%d").date()
                    for line in fh:
                        pass
                    ds = line.split(",")[0]
                    tl[1] = datetime.strptime(ds,"%Y.%m.%d").date()

                if pair in self.datadict:
                    self.datadict[pair].update({tf:tl})
                else:
                    self.datadict[pair] = {tf:tl}




class slideAndNum(QWidget):

    def __init__(self, settCode,name, max_val, min_val, default, step):
        QWidget.__init__(self)
        self.settCode = settCode
        self.value = default

        self.maximum = max_val
        self.minimum = min_val
        self.default = default
        self.stepsize = step

        self.label = QLabel(name)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.valLabel = QLabel(str(self.value))
        self.makeSlider()


        lay = QHBoxLayout()
        lay.addWidget(self.label)
        lay.addWidget(self.slider)
        lay.addWidget(self.valLabel)
        self.setLayout(lay)

    def setValue(self,valueDict):
        value = float(valueDict.values()[0])
        self.updateSlider(value)

    def getSetting(self):
        return {self.settCode:self.value}

    def makeSlider(self):
        self.slider = QSlider()
        self.slider.setOrientation(Qt.Horizontal)
        stps = int((self.maximum-self.minimum)/self.stepsize)
        self.slider.setMaximum(stps)
        self.slider.valueChanged.connect(self.updateVal)
        self.updateSlider(self.default)

    def updateSlider(self,value):
        dfv = int((value-self.minimum)/self.stepsize)
        self.slider.setValue(dfv)

    def updateVal(self,value):
        self.value = str(value*self.stepsize+self.minimum)
        self.valLabel.setText(self.value)

class comboSetting(QWidget):

    def __init__(self,settCode,name):
        QWidget.__init__(self)
        self.settCode = settCode

        lay = QHBoxLayout()
        self.setLayout(lay)
        self.lab = QLabel(name)
        self.lab.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.comboB = QComboBox()

        lay.addWidget(self.lab)
        lay.addWidget(self.comboB)
        lay.setStretch(0,1)
        lay.setStretch(1,4)

    def setValue(self,valueDict):
        value = valueDict.values()[0]
        self.comboB.setCurrentIndex(self.comboB.findText(value))

    def getSetting(self):
        return {self.settCode:self.comboB.currentText()}

    def addItems(self,itemlist):
        self.comboB.clear()
        self.comboB.addItems(itemlist)

class dateRange(QGroupBox):

    def __init__(self,settCode,name,min_date,max_date):
        QGroupBox.__init__(self,name)
        self.settCode = settCode

        self.maxDate = max_date
        self.minDate = min_date

        self.startDateW = QDateEdit(self.minDate)
        self.endDateW = QDateEdit(self.maxDate)

        self.graphW = QGraphicsView()
        self.updateDateInputs()
        self.updateGraphic()
        self.graphW.setStyleSheet("background: transparent; border: transparent;")
        self.graphW.setMinimumWidth(300)

        lay = QGridLayout()
        lay.addWidget(self.startDateW,0,0)
        lay.addWidget(self.endDateW,1,0)
        lay.addWidget(self.graphW,0,1,2,1)
        self.setLayout(lay)

    def setValue(self,valueDict):
        if "_start" in valueDict.keys()[0]:
            startVal = valueDict[self.settCode+"_start"]
            startDate = QDate.fromString(startVal, "yyyy-MM-dd")
            self.startDateW.setDate(startDate)
        elif "_end" in valueDict.keys()[0]:
            endVal = valueDict[self.settCode+"_end"]
            endDate = QDate.fromString(endVal, "yyyy-MM-dd")
            self.endDateW.setDate(endDate)

    def getSetting(self):
        kF = self.settCode+"_start"
        kT = self.settCode+"_end"
        dF = str(self.startDateW.date().toString(Qt.ISODate))
        dT = str(self.endDateW.date().toString(Qt.ISODate))
        return {kF:dF,kT:dT}

    def updateDateInputs(self):

        self.startDateW.setDate(self.minDate)
        self.endDateW.setDate(self.maxDate)
        self.startDateW.setDateRange(self.minDate,self.maxDate)
        self.endDateW.setDateRange(self.minDate,self.maxDate)
        self.startDateW.dateChanged.connect(self.updateGraphic)
        self.endDateW.dateChanged.connect(self.updateGraphic)

    def updateGraphic(self):
        scene = QGraphicsScene(0,0,300,25)
        h = scene.height()
        vc = h/2
        w = scene.width()
        dr = float((self.maxDate-self.minDate).days)

        totdays = (self.endDateW.date().toPyDate()-self.startDateW.date().toPyDate()).days
        ds = (((self.startDateW.date().toPyDate()-self.minDate).days)/dr)*w
        dw = (totdays/dr)*w

        pen =QPen()
        brush = QBrush(QColor(Qt.blue),Qt.SolidPattern)

        scene.addLine(0,vc,w,vc)
        scene.addRect(ds,0,dw,h,brush=brush)

        self.graphW.setScene(scene)


def main():
    app = QApplication(sys.argv)
    app.setStyle("plastique")
    window = mainWindow()
    window.showMaximized()
    sys.exit(app.exec_())

if __name__==("__main__"):
    main()