#!/usr/bin/env python3

"""
This function takes varying initial conditions and returns store.
"""

import numpy as np
import time
import pickle
import matplotlib.pyplot as plt
import argparse 

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--n", type=int, default = 10,
                    help="number of samples in the grid search, defaults to 10")

def simulate(ICs, timeStep, time):
  from simulator import Simulator
  from store import QRangeStore

  vel1 = ICs[0]
  vel2 = ICs[1]
  pos  = ICs[2]
  m1   = 50
  m2   = 50

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

def runGridSearch(n):
  rng = np.random.default_rng(seed=3)
  #n   = 1000 #Number of samples
  matrix = rng.uniform(-100, 100, size=(3,3,n))
  
  
  IC = [matrix[:,0], matrix[:,1], matrix[:,2]]
  timeStep = 0.01
  Time     = 0
  
  t0 = time.time()
  
  minMaxVals = np.zeros((2,n))
  for i in range(n):
      IC = [matrix[:,0,i], matrix[:,1,i], matrix[:,2,i]]
      minDist, maxDist = simulate(IC, timeStep, Time)
      minMaxVals[0,i] = minDist
      minMaxVals[1,i] = maxDist
  print(minMaxVals)
  
  t1 = time.time()
  print(t1-t0)
  # Save our results.
  fileName = f"gridSearchn{n}.pickle"
  with open(fileName, "wb") as f:
      pickle.dump(minMaxVals, f)
  
  # Absolute magnitude of velocities on x, y axes
  # Color = Max Dis between agents during sim 
  colMax = minMaxVals[1,:]
  vel1 = np.linalg.norm(matrix[:,0,:], axis=0)
  vel2 = np.linalg.norm(matrix[:,1,:], axis=0)
  plt.scatter(vel1, vel2, c=colMax, cmap='viridis')
  plt.colorbar(label='Max Distance between Agents during Sim')
  plt.xlabel(r'$||\hat{v}_1||^2$')
  plt.ylabel(r'$||\hat{v}_2||^2$')
  plt.title('Effect of Magnitudes of Agents\' Initial Velocities\n on Max Distance between Agents during Sim')
  plt.savefig(f"VelMagsMaxDistn{n}", dpi=300, bbox_inches="tight")
  plt.show()
  
  colMin = minMaxVals[0,:]
  fig = plt.figure()
  ax = fig.add_subplot(111, projection='3d')
  sc = ax.scatter(matrix[0,2,:],matrix[1,2,:],matrix[2,2,:], c=colMin, cmap='viridis')
  plt.colorbar(sc, label='Min Distance between Agents during Sim', pad=0.15)
  ax.set_xlabel(r'$\hat{r}_{2,x}$')
  ax.set_ylabel(r'$\hat{r}_{2,y}$')
  ax.set_zlabel(r'$\hat{r}_{2,z}$')
  ax.set_title('$\hat{r}_2$ vs. Min Distance between Agents during Sim')
  plt.tight_layout()
  plt.savefig(f"R2MinDistn{n}", dpi=300, bbox_inches="tight")
  plt.show()
 
if __name__ == "__main__":
    args = parser.parse_args()
    runGridSearch(args.n)
