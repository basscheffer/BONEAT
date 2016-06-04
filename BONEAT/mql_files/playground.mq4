//+------------------------------------------------------------------+
//|                                                   playground.mq4 |
//|                        Copyright 2015, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2015, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
//+------------------------------------------------------------------+
//| Script program start function                                    |
//+------------------------------------------------------------------+
#include <NEAT\brain.mqh>
#include <NEAT\tools.mqh>
void OnStart()
  {
      string filepath = "AUDUSD_240.gt.txt";
      NNGenome genotype(filepath);
      NeuralNetwork NN(genotype);
      double O = 0.673;double H = 0.6767;double L = 0.671;double C = 0.67300;double C1=0.6759;
      datetime date = StringToTime("2000.04.02 04:00");
      int open_order_dir = 1; double open_order_profit = 0.0025;
      int order = NN.getAction(O,H,L,C,C1,date,open_order_dir,open_order_profit);
      Print(order);
  };
//+------------------------------------------------------------------+
