//+------------------------------------------------------------------+
//|                                                        brain.mq4 |
//|                        Copyright 2015, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property library
#property copyright "Copyright 2015, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
#property strict
//+------------------------------------------------------------------+
//| Structs                                                          |
//+------------------------------------------------------------------+
struct Norm{
   string name;
   double value;
};
struct NGene
{
   int name;
   int type;
   int io;
};
struct LGene{
   int fromNeuron;
   int toNeuron;
   double weight;
};
struct Link
{
   int fromNeuron;
   double weight;
};
//+------------------------------------------------------------------+
//| Genome Clas                                                      |
//+------------------------------------------------------------------+
class NNGenome
{
public:
   string pair;
   int timefrme;
   double network_version;
   Norm l_norm[];
   LGene l_links[];
   NGene l_neurons[];
   NNGenome(){};
   NNGenome(string filepath){MakeFromFile(filepath);};
   void MakeFromFile(string file_path)
   {
   string mode;
   
   // open the file
   int fh = FileOpen(file_path,FILE_READ|FILE_TXT);
   // read each line in the code
   while(!FileIsEnding(fh))
   {
     string line = FileReadString(fh);
     // get the first character of the line and check if it's a '>'
     int fc = StringGetChar(line,0);
     if(fc==62)
     {
       // if so switch the mode to the value
       mode = StringSubstr(line,1);
       continue;// don't process this line
     };
     // split the line
     string split[];
     StringSplit(line,';',split);
     // switch between different modes
     if(mode=="PROP")
     {   
         if(split[0]=="PAIR") pair = split[1];
         else if(split[0]=="TF") timefrme = StrToInteger(split[1]);
         else if(split[0]=="VERS") network_version = StrToDouble(split[1]);
     }
     else if(mode=="PREP")
     {
         int oS = ArraySize(l_norm);
         ArrayResize(l_norm,oS+1);
         l_norm[oS].name = split[0];
         l_norm[oS].value = StringToDouble(split[1]);
     }
     else if(mode=="NEUR")
     {
         int oS = ArraySize(l_neurons);
         ArrayResize(l_neurons,oS+1);
         l_neurons[oS].name = StrToInteger(split[0]);
         l_neurons[oS].type = StrToInteger(split[1]);
         l_neurons[oS].io = StrToInteger(split[2]);
     }
     else if(mode=="LINK")
     {
         int oS = ArraySize(l_links);
         ArrayResize(l_links,oS+1);
         l_links[oS].fromNeuron = StrToInteger(split[0]);
         l_links[oS].toNeuron = StrToInteger(split[1]);
         l_links[oS].weight = StrToDouble(split[2]);
     };
   };
   FileClose(fh);   
   };   
};
//+------------------------------------------------------------------+
//| Neuron Class                                                     |
//+------------------------------------------------------------------+
class Neuron
{
public:
   int type;
   int io;
   int name;
   double inSum;
   double output;
   Link links[];

   Neuron(){};
   Neuron(int _name,int _type,int _io)
   {  
      name = _name;
      type = _type;
      io = _io;
   };
   void AddLink(int _from_neuron, double _weight)
   {
      int oldSize = ArraySize(links);
      ArrayResize(links,oldSize+1);
      links[oldSize].fromNeuron = _from_neuron;
      links[oldSize].weight = _weight;
   };
   double activate()
   {
      output = (exp(inSum)-exp(-inSum))/(exp(inSum)+exp(-inSum));
      return(output);
   };
};
//+------------------------------------------------------------------+
//| Pre Processor class                                              |
//+------------------------------------------------------------------+
class PreProcessor
{
public:
   double O_N, H_N, L_N, C_N, P_N;
   PreProcessor(Norm &_norm_list[])
   {   
      O_N = getValue("OPEN",_norm_list);
      H_N = getValue("HIGH",_norm_list);
      L_N = getValue("LOW",_norm_list);
      C_N = getValue("CLOSE",_norm_list);
      P_N = getValue("PROFIT",_norm_list);      
   };
   void processInput(double _O,
                     double _H,
                     double _L,
                     double _C,
                     double _C1,
                     datetime _date,
                     int _open_order_dir,
                     double _open_order_profit,
                     double &_return_list[])
   {
      _return_list[0] = TimeDayOfYear(_date)/365.0; // TOY
      _return_list[1] = TimeHour(_date)/24.0; // TOD
      _return_list[2] = (_O-_C1)/O_N; // open
      _return_list[3] = (_H-_O)/H_N; // high
      _return_list[4] = (_L-_O)/L_N; // low
      _return_list[5] = (_C-_O)/C_N; // close
      _return_list[6] = checkOpenPos(_open_order_dir); // open position
      _return_list[7] = double(_open_order_dir); // position direction
      _return_list[8] = _open_order_profit/P_N; // position profit
   };
   
   double checkOpenPos(int _pos_dir)
   {
      if(_pos_dir!=0.0){return(1.0);}
      else{return(0.0);};      
   };             
   
   
   double getValue(string key, Norm &norm_list[])
   {
      for(int i=0;i<ArraySize(norm_list);i++)
      {
         if(norm_list[i].name == key) 
            return(norm_list[i].value);
         
      };
      return(-1.0);
   };
};

//+------------------------------------------------------------------+
//| Neural Networrk Class                                            |
//+------------------------------------------------------------------+
class NeuralNetwork
{
public:
   NNGenome *genome;
   double outputs[];
   double inputs[];
   Neuron *neurons[];
   PreProcessor *preP;
   
   ~NeuralNetwork(){removeNeuronPointers();};
   NeuralNetwork(NNGenome &_genome){buildNetwork(_genome);};
   
   int getAction(double _O,
                  double _H,
                  double _L,
                  double _C,
                  double _C1,
                  datetime _date,
                  int _open_order_dir,
                  double _open_order_profit)
   {
   preP.processInput(_O,_H,_L,_C,_C1,_date,_open_order_dir,_open_order_profit,inputs);
   updateNetwork();
   int ans = postProcess();
   return(ans);
   };
   
   void buildNetwork(NNGenome &_genome)
   {
      genome = GetPointer(_genome);
      preP = new PreProcessor(_genome.l_norm);

      //build all the neurons
      for(int i=0;i<ArraySize(genome.l_neurons);i++)
      {
         int name = genome.l_neurons[i].name;
         int io = genome.l_neurons[i].io;
         int type = genome.l_neurons[i].type;
         if(type==2) addOutput();
         else if(type==1) addInput();          
         Neuron *N = new Neuron(name,type,io);
         addNeuron(N);
      };
      //add all the links
      for(int i=0;i<ArraySize(genome.l_links);i++)
      {
         int from = genome.l_links[i].fromNeuron;
         int to = genome.l_links[i].toNeuron;
         double weight = genome.l_links[i].weight;
         int nI = getNeuronIndex(to);
         neurons[nI].AddLink(from,weight);     
      };
   };
   void updateNetwork()
   {
      // set the input and bias neurons values
      for(int i=0;i<ArraySize(neurons);i++)
      {
         if(neurons[i].type==0) neurons[i].output = 1.0;
         else if(neurons[i].type==1) 
            neurons[i].output = inputs[neurons[i].io-1];
      };
      // calculate all input sums
      for(int i=0;i<ArraySize(neurons);i++)
      {
         neurons[i].inSum = 0.0;
         for(int ii=0;ii<ArraySize(neurons[i].links);ii++)
         {
            double val = getNeuronValue(neurons[i].links[ii].fromNeuron);
            neurons[i].inSum += val;
         };
      };
      // calculate all activations
      for(int i=0;i<ArraySize(neurons);i++)
      {
         neurons[i].activate();
         // and add the result to the output list
         if(neurons[i].type == 3) 
            outputs[neurons[i].io-1] = neurons[i].output;
      };
   };
   int postProcess()
   {
      bool open_buy = false;
      bool open_sell = false;
      bool close_pos = false;
      //0->open buy 1->open sell 2->close position
      if(outputs[0]>0.5) open_buy = true;
      if(outputs[1]>0.5) open_sell = true;
      if(outputs[2]>0.5) close_pos = true;
      //action output: 0->no action 1->open buy 2->open sell 3->close position
      if(open_buy==open_sell)
      {
         if(close_pos) return(3);
         else return(0);
      }
      else if(open_buy) return(1);
      else if(open_sell) return(2);
      else return(0);
   };
   void addInput()
   {
      int oS = ArraySize(inputs);
      ArrayResize(inputs,oS+1);
      inputs[oS]=0.0;
   };
   void addOutput()
   {
      int oS = ArraySize(outputs);
      ArrayResize(outputs,oS+1);
      outputs[oS]=0.0;
   };
   void addNeuron(Neuron *_neuron)
   {
      int oS = ArraySize(neurons);
      ArrayResize(neurons,oS+1);
      neurons[oS] = _neuron;
   };
   int getNeuronIndex(int _neuronName)
   {
      for(int i=0;i<ArraySize(neurons);i++)
      {
         if(neurons[i].name == _neuronName)return(i);
      };
      return(-1);
   };
   double getNeuronValue(int _neuronName)
   {
      int idx = getNeuronIndex(_neuronName);
      return(neurons[idx].output);
   };
   void removeNeuronPointers()
   {
   for(int i=0;i<ArraySize(neurons);i++)delete(neurons[i]);
   delete preP;
   };
};

//+------------------------------------------------------------------+
//| My function                                                      |
//+------------------------------------------------------------------+
//+------------------------------------------------------------------+
//| My function                                                      |
//+------------------------------------------------------------------+