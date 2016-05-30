import pandas as pd
import numpy as np
import multiprocessing as mp
from phenotype import *
import time
import math
from datetime import *

# def get_input_data(data_path='data/AUDUSD240.csv',start_date = '1999-12-31', end_date = '2007-05-01'):
#     df = pd.read_csv(data_path, sep=',')
#     df['date'] = pd.to_datetime(df['date'],format="%Y.%m.%d")
#
#     df = df[(df['date'] >= start_date) & (df['date'] < end_date)].reset_index()
#
#     da = np.zeros((len(df.index),7))
#
#     for row in df.itertuples():
#
#         if row.Index == 0:
#             O = 0.0
#         else:
#             O = row.open-df.ix[row.Index-1]['open']
#         H = row.high-row.open
#         L = row.low-row.open
#         C = row.close-row.open
#         TOD = float(row.time.split(':')[0])+4.0
#         TOY = row.date.timetuple().tm_yday
#         open_price = row.open
#
#         da[row.Index,0] = TOY
#         da[row.Index,1] = TOD
#         da[row.Index,2] = O
#         da[row.Index,3] = H
#         da[row.Index,4] = L
#         da[row.Index,5] = C
#         da[row.Index,6] = open_price
#
#
#     NTOY = da[:,0]/365.0
#     NTOD = da[:,1]/24.0
#     NO = da[:,2]/max(abs(da[:,2]))
#     NH = da[:,3]/max(abs(da[:,3]))
#     NL = da[:,4]/max(abs(da[:,4]))
#     NC = da[:,5]/max(abs(da[:,5]))
#     OP = da[:,6]
#
#     cols = (NTOY,NTOD,NO,NH,NL,NC,OP)
#
#     norm_data = np.column_stack(cols)
#
#     return norm_data

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

    def runSimulation(self,data,neuralNetwork):

        NN = neuralNetwork

        for tf in data:
            openbuy=False
            opensell=False
            closepos=False

            openprice = tf[1]
            self.updatePosProfit(openprice)

            #CONSTANT
            posprof = self.pos_prof/0.627450
            inputlist = [self.pos_open,self.pos_dir,posprof]
            inputlist.extend(tf[2:8])

            outputlist = NN.update(inputlist)

            if outputlist[0] > 0.5:
                openbuy = True
            if outputlist[1] > 0.5:
                opensell = True
            if outputlist[2] > 0.5:
                closepos = True

            if (openbuy and opensell) or (not openbuy and not opensell):
                if closepos:
                    self.closePosition()
            else:
                if openbuy and not opensell:
                    self.openPosition(1.0,openprice)
                else:
                    self.openPosition(-1.0,openprice)

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

        return perf

    def openPosition(self,direction,price):
        if self.pos_open == 0.0:
            self.pos_open = 1.0
            self.pos_dir = direction
            self.pos_price = price

    def updatePosProfit(self,currentPrice):
        #CONSTANT
        spread = 0.00018
        profit = (self.pos_price-currentPrice)*self.pos_dir
        self.pos_prof = profit-spread

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

def simuRoutine(process_data):

    data = np.load(process_data[1])
    NN = neuralNetwork(process_data[0])
    SIM = Simulator()
    return SIM.runSimulation(data,NN)

def fastSimulate(list_of_genomes,data_file_path,processes=1):

    processing_list = []

    # make a NN from each genome and append it to a processing list
    for genome in list_of_genomes:
        processing_list.append([genome,data_file_path])

    pool = mp.Pool(processes)
    cz =int(math.ceil(len(processing_list)/float(processes)))
    resultlist = pool.map(simuRoutine,processing_list,chunksize=cz)
    pool.close()
    pool.join()

    worst_perf = min(r['p2/dd'] for r in resultlist)

    for perf in resultlist:
        perf["fitness"]=perf['p2/dd']-worst_perf

    for i,genome in enumerate(list_of_genomes):
        genome.fitness = resultlist[i]['fitness']
        genome.performance = resultlist[i]

    best_performer = max(resultlist,key=lambda r: r['fitness'])
    print "Best performer:"
    for key in best_performer:
        print key," : ",best_performer[key]

def slowSimulate(list_of_genomes,data_file_path):
    #### WATCH OUT NOT UP TO DATE

    # make a NN from each genome and append it to a processing list
    for genome in list_of_genomes:
        result = simuRoutine([genome,data_file_path])
        if genome.fitness > 0.0 and genome.fitness != result["fitness"]:
            print "\n############ WARNING ############\n"
        genome.fitness = result['fitness']
        genome.performance = result

    best_performer = max(list_of_genomes,key=lambda g: g.fitness)
    print "Maximum fitness = %.1f with performance:" %best_performer.fitness
    print best_performer.performance

# if __name__=='__main__':
#     makeBacktestData()
#     arr = np.load("data/AUDUSD240_NormData.npy")
#     print arr[1017:1020]