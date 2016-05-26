import pandas as pd
import numpy as np
import multiprocessing as mp
from phenotype import *
import time
import math

def get_input_data(data_path='data/AUDUSD240.csv',start_date = '1999-12-31', end_date = '2007-05-01'):
    #TODO auto recognise timeframe
    df = pd.read_csv(data_path, sep=',')
    df['date'] = pd.to_datetime(df['date'],format="%Y.%m.%d")

    df = df[(df['date'] >= start_date) & (df['date'] < end_date)].reset_index()

    da = np.zeros((len(df.index),7))

    for row in df.itertuples():

        if row.Index == 0:
            O = 0.0
        else:
            O = row.open-df.ix[row.Index-1]['open']
        H = row.high-row.open
        L = row.low-row.open
        C = row.close-row.open
        TOD = float(row.time.split(':')[0])+4.0
        TOY = row.date.timetuple().tm_yday
        open_price = row.open

        da[row.Index,0] = TOY
        da[row.Index,1] = TOD
        da[row.Index,2] = O
        da[row.Index,3] = H
        da[row.Index,4] = L
        da[row.Index,5] = C
        da[row.Index,6] = open_price


    NTOY = da[:,0]/365.0
    NTOD = da[:,1]/24.0
    NO = da[:,2]/max(abs(da[:,2]))
    NH = da[:,3]/max(abs(da[:,3]))
    NL = da[:,4]/max(abs(da[:,4]))
    NC = da[:,5]/max(abs(da[:,5]))
    OP = da[:,6]

    cols = (NTOY,NTOD,NO,NH,NL,NC,OP)

    norm_data = np.column_stack(cols)

    return norm_data

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

            openprice = tf[6]
            self.updatePosProfit(openprice)

            inputlist = [self.pos_open,self.pos_dir,self.pos_prof]
            inputlist.extend(tf[:6])

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
            perf['fitness'] = self.curr_bal/self.max_dd
        else:
            perf['fitness'] = self.curr_bal
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
            self.trade_count+=1

    def updatePosProfit(self,currentPrice):
        profit = (self.pos_price-currentPrice)*self.pos_dir
        self.pos_prof = profit

    def closePosition(self):
        if self.pos_open > 0.0:
            self.curr_bal += self.pos_prof
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

    for i,genome in enumerate(list_of_genomes):
        genome.fitness = resultlist[i]['fitness']
        genome.performance = resultlist[i]

    best_performer = max(resultlist,key=lambda r: r['fitness'])
    print "Maximum fitness = %.1f with performance:" %best_performer['fitness']
    print best_performer

def makeTestDataFile(filename,start_date = '1999-12-31',end_date = '2007-05-01'):

    arr = get_input_data(start_date=start_date,end_date=end_date)
    np.save(filename,arr)




