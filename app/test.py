#!/usr/bin/env python3

"""
NOTE: Test the simulator locally. First build the `queries` binary with `cargo build --release` and then run this script.
"""

from modsim import data
from simulator import Simulator
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
print(f"{len(store)=}")
print("1\n")
print(store[1])
print("500\n")
print(store[500])
print("1000\n")
print(store[1000])
print("1001\n")
print(store[1001])
