#!/usr/bin/env python3

"""
This function takes varying initial conditions and returns store.
"""

import numpy as np

def simulate(ICs, timeStep, time):
  from simulator import Simulator
  from store import QRangeStore

  vel1 = ICs[0]
  vel2 = ICs[1]
  pos  = ICs[2]
  m1   = ICs[3]
  m2   = ICs[4]

  data = {
      'Body1': {
          'timeStep': timeStep,
          'time': time,
          'position': {'x':       0, 'y':       0, 'z':       0},
          'velocity': {'x': vel1[0], 'y': vel1[1], 'z': vel1[2]},
          'mass': m1
      },
      'Body2': {
          'timeStep': timeStep,
          'time': time,
          'position': {'x':  pos[0], 'y':  pos[1], 'z':  pos[2]},
          'velocity': {'x': vel2[0], 'y': vel2[1], 'z': vel2[2]},
          'mass': m2 
      }
}
  store = QRangeStore()
  sim = Simulator(store, data)
  sim.simulate()
  

  d  = {}
  for i in range(len(store)):
    l1 = list(store[i][0].values())
    l2 = list(store[i][1].values())
    key1 = l1[0]['time']
    key2 = l2[0]['time']
   
    if key1==key2:
      l = np.array(list(l1[0]['position'].values()))-np.array(list(l2[0]['position'].values()))
      d[key1] = np.linalg.norm(l)
    else:
      raise Exception("The times of the two agents are mis-matched.")  
  minDist = min(list(d.values()))
  maxDist = max(list(d.values()))
  return minDist, maxDist
