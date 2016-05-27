# BONEAT
options trading with NEAT

So basically it is a NEAT as desriped here: http://nn.cs.utexas.edu/downloads/papers/stanley.ec02.pdf
That should serve as comments too, sorry....

It builds a population of trading neural networks
through genetic optimisation and specification it generates better new generations of trading robots

a robot takes as input:
  - difference betwee open price and last close price normalised
  - difference between high and open normalised
  - difference between low and open normalised
  - difference between close and open normalised
  - time of day normalised
  - time of year normalised
  - open position (1.0 -> yes there is an open position, 0.0 -> no)
  - position direction (-1.0 -> sell, 1.0 -> buy)
  - position profit
  
a robot has three possible actions
  - open buy position
  - open sell position
  - close position
  
a robot can have a memory (not necesseraly) 
so just creating a phenotype or network and activating it from a genotype 
might give different behaviour and it should be handed some history data
it is possible to save a network in an activated state but currently not implemented
  
