import numpy as np
import multiprocessing as mp
from phenotype import *
import time
import math
from datetime import *
import dateutil.parser as dp

def makeBacktestData(data_path='data/AUDUSD240.csv'):

    datefunc = lambda x: datetime.strptime(x, '%Y.%m.%d')
    timefunc = lambda x: int(x.split(':')[0])
    da = np.genfromtxt(data_path, delimiter=',',
              converters={0: datefunc,1:timefunc}, dtype='object,|i2,float,float,float,float',
              names=["date", "time", "open", "high", "low", "close"],
              usecols=(0,1,2,3,4,5),
              skip_header=1)

    DATE = da[:]["date"]
    PRICE = np.zeros(da.size)
    TOY  = np.zeros(da.size)
    TOD = da[:]["time"]
    O = np.zeros(da.size)
    H = np.zeros(da.size)
    L = np.zeros(da.size)
    C = np.zeros(da.size)

    for i in range(da.size):
        TOY[i] = da[i]["date"].timetuple().tm_yday
        if i < da.size-1:
            PRICE[i] = da[i+1]["open"]
        if i > 0:
            O[i] = da[i]["open"]-da[i-1]["close"]
        H[i] = da[i]["high"]-da[i]["open"]
        L[i] = da[i]["low"]-da[i]["open"]
        C[i] = da[i]["close"]-da[i]["open"]

    cO = max(abs(O))
    cH = max(abs(H))
    cL = max(abs(L))
    cC = max(abs(C))
    cP = max(PRICE)-min(PRICE[:-2])

    cols = (DATE,
            PRICE,
            TOY/365.0,
            TOD/24.0,
            O/cO,H/cH,L/cL,C/cC)

    norm_data = np.column_stack(cols)

    data_file = data_path.split('.')[0]+"_NormData.npy"
    norm_const_file = data_path.split('.')[0]+"_NormConst.txt"
    with open(norm_const_file,mode="w") as fh:
        fh.write("O;%f\n"%cO)
        fh.write("H;%f\n"%cH)
        fh.write("L;%f\n"%cL)
        fh.write("C;%f\n"%cC)
        fh.write("P;%f\n"%cP)

    print norm_data
    np.save(data_file,norm_data)

class Simulator:

    def __init__(self):
        self.pos_open = 0.0
        self.pos_dir = 0.0
        self.pos_prof = 0.0
        self.pos_price = 0.0

        self.max_bal = 0.0
        self.curr_bal = 0.0
        self.max_dd = 0.0
        self.trade_count = 0
        self.win_count = 0

    def runSimulation(self,data,neuralNetwork,settings):

        NN = neuralNetwork

        for i,tf in enumerate(data):
            openbuy=False
            opensell=False
            closepos=False

            openprice = tf[1]
            if self.pos_open != 0.0:
                self.updatePosProfit(openprice,float(settings["spread"]))

            posprof = self.pos_prof/settings["profit_norm"]
            inputlist = [self.pos_open,self.pos_dir,posprof]
            inputlist.extend(tf[2:8])
            outputlist = NN.update(inputlist)

            if i <= 30:
                continue

            if outputlist[0] > 0.0:
                openbuy = True
            if outputlist[1] > 0.0:
                opensell = True
            if outputlist[2] > 0.0:
                closepos = True

            outsum = sum((openbuy,opensell,closepos))
            if outsum == 1:
                if openbuy:
                    self.openPosition(1.0,openprice)
                elif opensell:
                    self.openPosition(-1.0,openprice)
                elif closepos:
                    self.closePosition()
            elif outsum == 2:
                if openbuy and closepos:
                    self.openPosition(1.0,openprice)
                elif opensell and closepos:
                    self.openPosition(-1.0,openprice)
                else:
                    pass
            else:
                pass

        return self.getPerformance()

    def getPerformance(self):
        perf = {'winratio':0.0}
        if self.max_dd > 0.0:
            perf['prof/dd'] = self.curr_bal/self.max_dd
            perf['p2/dd'] = (self.curr_bal*abs(self.curr_bal))/self.max_dd
        else:
            perf['prof/dd'] = self.curr_bal*abs(self.curr_bal)
            perf['p2/dd'] = self.curr_bal
        perf['profit'] = self.curr_bal
        perf['drawdown'] = self.max_dd
        perf['trades'] = self.trade_count
        if self.trade_count > 0:
            perf['winratio'] = float(self.win_count)/float(self.trade_count)
        perf["t*p2/d"] = self.trade_count*perf["p2/dd"]

        return perf

    def openPosition(self,direction,price):
        if self.pos_open == 1.0:
            if self.pos_dir == direction:
                return
            else:
                self.closePosition()
        self.pos_open = 1.0
        self.pos_dir = direction
        self.pos_price = price

    def updatePosProfit(self,currentPrice,spread):

        profit = (currentPrice-self.pos_price)*self.pos_dir
        self.pos_prof = profit-(spread/10000)

    def closePosition(self):
        if self.pos_open > 0.0:
            self.curr_bal += self.pos_prof
            self.trade_count+=1
            if self.pos_prof > 0.0:
                self.win_count+=1
            self.calcExtremes()
            self.pos_open = 0.0
            self.pos_dir = 0.0
            self.pos_prof = 0.0
            self.pos_price = 0.0

    def calcExtremes(self):
        if self.curr_bal > self.max_bal:
            self.max_bal = self.curr_bal
        if self.max_bal-self.curr_bal > self.max_dd:
            self.max_dd=self.max_bal-self.curr_bal

def getData(data_path,settings,data_field = "train"):
    A = np.load(data_path)

    if data_field == "train":
        from_date=dp.parse(settings["traindata_start"])
        to_date=dp.parse(settings["traindata_end"])
    elif data_field == "confirm":
        from_date=dp.parse(settings["confirmdata_start"])
        to_date=dp.parse(settings["confirmdata_end"])
    else:
        raise NameError("data field %s not defined"%data_field)
    # idx=(A[:,0]>=from_date) & (A[:,0]<to_date)
    # return(A[idx])

    si = min(np.where(A[:,0]>=from_date)[0])-1
    ei = min(np.where(A[:,0]>=to_date)[0])
    return (A[si:ei])

def simuRoutine(process_data):

    data = getData(process_data[1],process_data[2])
    NN = neuralNetwork(process_data[0])
    S = process_data[2]
    SIM = Simulator()
    return SIM.runSimulation(data,NN,S)

def confirmRoutine(process_data):
    data = getData(process_data[1],process_data[2],"confirm")
    NN = neuralNetwork(process_data[0])
    S = process_data[2]
    SIM = Simulator()
    return SIM.runSimulation(data,NN,S)

def fastSimulate(list_of_genomes,settings):

    processes = int(settings["cores"])
    data_file_path = settings["test_data_path"]
    processing_list = []

    # make a NN from each genome and append it to a processing list
    for genome in list_of_genomes:
        processing_list.append([genome,data_file_path,settings])

    pool = mp.Pool(processes)

    resultlist = pool.map(simuRoutine,processing_list)
    pool.close()
    pool.join()

    p_mode = settings["perf_mode"]

    for perf in resultlist:
        fit = perf[p_mode]
        if fit < 0.0:
            fit = -0.0001
        perf["fitness"] = fit+0.0001

    for i,genome in enumerate(list_of_genomes):
        genome.fitness = resultlist[i]['fitness']
        genome.performance = resultlist[i]

    best_performer = max(resultlist,key=lambda r: r[p_mode])
    print "Best performer:"
    for key in best_performer:
        print key," : ",best_performer[key]

def fastSimulateConfirm(list_of_genomes,settings):

    processes = int(settings["cores"])
    data_file_path = settings["test_data_path"]
    processing_list = []

    # make a NN from each genome and append it to a processing list
    for genome in list_of_genomes:
        processing_list.append([genome,data_file_path,settings])

    pool = mp.Pool(processes)

    resultlist = pool.map(simuRoutine,processing_list)
    pool.close()
    pool.join()

    p_mode = settings["perf_mode"]

    for perf in resultlist:
        fit = perf[p_mode]
        if fit <= 0.0:
            fit = -0.0001
        perf["fitness"] = fit+0.0001
        

    confirm_genome_list = []

    for i,genome in enumerate(list_of_genomes):
        genome.fitness = resultlist[i]['fitness']
        genome.performance = resultlist[i]
        if genome.fitness > 0.0:
            confirm_genome_list.append(genome)

    processing_conf_list = []
    for genome in confirm_genome_list:
        processing_conf_list.append([genome,data_file_path,settings])

    pool = mp.Pool(processes)
    confirmlist = pool.map(confirmRoutine,processing_conf_list)
    pool.close()
    pool.join()

    for i,genome in enumerate(confirm_genome_list):
        cf = confirmlist[i][p_mode]
        change = cf/genome.performance[p_mode]
        genome.performance["confirmfactor"] = change
        if change > 1.0:
            change = 1.0
        if change < 0.0:
            change = 0.0
        genome.performance["fitness"] = genome.performance["fitness"]*change

    best_performer = max(list_of_genomes,key=lambda g: g.fitness)
    print "Best performer:"
    for key in best_performer.performance:
        print key," : ",best_performer.performance[key]

# if __name__=='__main__':
#     makeBacktestData()
#     arr = np.load("data/AUDUSD240_NormData.npy")
#     print arr[1017:1020]

