//+------------------------------------------------------------------+
//|                                                        tools.mqh |
//|                        Copyright 2015, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2015, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property strict

#include <NEAT\brain.mqh>
//+------------------------------------------------------------------+
//| Print array                                                      |
//+------------------------------------------------------------------+
void printNetwork(NeuralNetwork &NN)
{
   for(int i=0;i<ArraySize(NN.neurons);i++)
   {
      string ts = StringFormat("Neuron %i with type %i and io %i",NN.neurons[i].name,NN.neurons[i].type,NN.neurons[i].io);
      for(int ii=ArraySize(NN.neurons[i].links)-1;ii>=0;ii--)
      {
         string ts2 = StringFormat("   Link from %i with weight %f"
               ,NN.neurons[i].links[ii].fromNeuron
               ,NN.neurons[i].links[ii].weight);
         Print(ts2);
      };
      Print(ts);
   };
};