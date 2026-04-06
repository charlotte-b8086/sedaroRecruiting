#!/usr/bin/env python3

"""
NOTE: Test the simulator locally. First build the `queries` binary with `cargo build --release` and then run this script.
"""

from modsim import data
from simulator import Simulator
from simulatorPropMass import Simulator as SimulatorPropMass
from store import QRangeStore

data = {
    'Body1': {
        'timeStep': 0.02,
        'time': 0.0,
        'position': {'x': -0.7, 'y': 0, 'z': 0},
        'velocity': {'x': 0, 'y': -0.0015, 'z': 0},
        'mass': 1
    },
    'Body2': {
        'timeStep': 0.01,
        'time': 0.0,
        'position': {'x': 60.34, 'y': 0, 'z': 0},
        'velocity': {'x': 0, 'y': 0.13 , 'z': 0},
        'mass': 0.123
    }
}

store = QRangeStore()
sim = Simulator(store, data)
sim.simulate()

m1 = {}
m2 = {}
for i in range(len(store)):
  l1 = list(store[i][0].values())
  l2 = list(store[i][1].values())
  key1 = l1[0]['time']
  key2 = l2[0]['time']

  if key1==key2:
    m1[key1] = l1[0]['mass']
    m2[key1] = l2[0]['mass']
  else:
    raise Exception("The times of the two agents are mis-matched.")

storePropMass = QRangeStore()
simPropMass = SimulatorPropMass(storePropMass, data)
simPropMass.simulate()

m1PropMass = {}
m2PropMass = {}
for i in range(len(storePropMass)):
  l1 = list(storePropMass[i][0].values())
  l2 = list(storePropMass[i][1].values())
  key1 = l1[0]['time']
  key2 = l2[0]['time']

  if key1==key2:
    m1PropMass[key1] = l1[0]['mass']
    m2PropMass[key1] = l2[0]['mass']
  else:
    raise Exception("The times of the two agents are mis-matched.")

print('Without Mass Propagation:\n')
print('Mass of Body1:')
print(m1)
print('\nMass of Body2:')
print(m2)

print('\n\n')

print('Propagating Mass with Rocket Law:\n')
print('Mass of Body1:')
print(m1PropMass)
print('\nMass of Body2:')
print(m2PropMass)
