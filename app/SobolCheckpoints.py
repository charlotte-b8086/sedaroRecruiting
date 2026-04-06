import os
import argparse
import pickle
import pandas as pd
from multiprocessing import Pool
from SALib.sample import sobol
from SALib.analyze import sobol as sobol_analyze
import numpy as np
import time
from datetime import timedelta
from ICSimulation import simulate
import matplotlib.pyplot as plt

'''
This code runs Sobol Sensitivity Analysis for varying the initial velocities and masses of the two agents,
and the initial position of the second agent. It uses parsers for 
the number of samples (2^n), the number of cores to use, and if 
you should be generating or analyzing the results (which includes plotting)
'''

default_n = os.cpu_count()
parser = argparse.ArgumentParser()
parser.add_argument("-N", type=int, default=1024,
                    help="obtain N*(2D+2) samples from parameter space")
parser.add_argument("-n", "--ncores", type=int, default = default_n,
                    help="number of cores, defaults to {} on this machine".format(default_n))
parser.add_argument("-m", "--mode", type=str, default = 'generate',
                    help="generate or analyze sobol samples")

# Each worker just runs the model with their parameter values 
def worker(parVals):
	return run_model(parVals)

def worker_unpack(args):
    return worker(*args)

def run_model(p):

    IC = [[p[0],p[1],p[2]], [p[3],p[4],p[5]], [p[6],p[7],p[8]], p[9], p[10]]
    # Run the model
    timeStep = 0.01
    Time = 0
    result = simulate(IC, timeStep, Time)

    assert len(result) == 2, "Unexpected number of outputs from ICSimulate.simulate()"

    minDist = result[0]
    maxDist = result[1]    
      
    return minDist, maxDist

def main(N, ncores=None, pool=None):
    if ncores is None:
        ncores = os.cpu_count()
    # Define the parameter space within the context of a problem dictionary
    problem = {
        # number of parameters
        'num_vars' : 11,
        # parameter names
        'names' : ['vel1x', 'vel1y', 'vel1z', 'vel2x', 'vel2y', 'vel2z', 'posx', 'posy', 'posz', 'm1', 'm2'], 
        # bounds for each corresponding parameter
        'bounds' : [
        [-100, 100],       # vel1x 
        [-100, 100],       # vel1y
        [-100, 100],       # vel1z
        [-100, 100],       # vel2x
        [-100, 100],       # vel2y
        [-100, 100],       # vel2z
        [-100, 100],       # posx
        [-100, 100],       # posy
        [-100, 100],       # posz
        [0, 1],            # m1
        [0, 1],            # m2
        ]
    }

    # Create the parameter combinations. 
    parVals = sobol.sample(problem, N, calc_second_order=True, seed=12345)
    
    # Run the sensitivity analysis!
    t0 = time.time()
    checkpoint_file = f"checkpoint_sobolN{N}.pickle"
    tasks =[list(p) for p in parVals]
    total_jobs = len(tasks)
    # ---load checkpoint if exists ---
    start_idx = 0
    output = []
    if os.path.exists(checkpoint_file):
      print("Loading checkpoint...")
      with open(checkpoint_file, "rb") as f:
        start_idx, output = pickle.load(f)
      print(f"Resuming from job {start_idx}/{total_jobs}")
    remaining_tasks =tasks[start_idx:]
    t_start = time.time()
    last_print = time.time()
    for i, result in enumerate(pool.imap_unordered(worker, remaining_tasks)):
      output.append(result)
      job_idx = start_idx + i + 1
# ---- progress display every ~10 sec ----
      if time.time() - last_print > 10:
            elapsed = time.time() - t_start
            rate = (i + 1) / elapsed if elapsed > 0 else 0
            remaining = total_jobs - job_idx
            eta = remaining / rate if rate > 0 else 0

            print(
                f"[{job_idx}/{total_jobs}] "
                f"{100*job_idx/total_jobs:.1f}% | "
                f"Elapsed {timedelta(seconds=int(elapsed))} | "
                f"ETA {timedelta(seconds=int(eta))}"
            )
            last_print = time.time()
####
      if job_idx % 50 == 0:
            print(f"Checkpointing at job {job_idx}")
            with open(checkpoint_file, "wb") as f:
                pickle.dump((job_idx, output), f)
    print('pooling is complete')

    validOutputs0 = [o[0] for o in output if o is not None and not np.isnan(o[0])]
    validOutputs1 = [o[1] for o in output if o is not None and not np.isnan(o[1])]
    if len(validOutputs0) == 0:
      raise ValueError("All simulations failed")
    if len(validOutputs1) == 0:
      raise ValueError("All simulations failed")
    meanValidOutputs0 = np.mean(validOutputs0)
    meanValidOutputs1 = np.mean(validOutputs1)
    output0Filled = [o[0] if o is not None and not np.isnan(o[0]) else meanValidOutputs0 for o in output]
    output1Filled = [o[1] if o is not None and not np.isnan(o[1]) else meanValidOutputs1 for o in output]
    t1 = time.time()
    print(t1-t0)

    # Save our results as a dictionary before we processes them. 
    fileName = f"unprocessed_sobolN{N}.pickle"
    with open(fileName, "wb") as f:
        result = {'minDist': np.array(output0Filled), 'maxDist': np.array(output1Filled), 'parVals': parVals}
        pickle.dump(result, f)

def analyze_sobol(N):
    # Define the parameter space within the context of a problem dictionary
    problem = {
        # number of parameters
        'num_vars' : 11,
        # parameter names
        'names' : ['vel1x', 'vel1y', 'vel1z', 'vel2x', 'vel2y', 'vel2z', 'posx', 'posy', 'posz', 'm1', 'm2'], 
        # bounds for each corresponding parameter
        'bounds' : [
        [-100, 100],       # vel1x 
        [-100, 100],       # vel1y
        [-100, 100],       # vel1z
        [-100, 100],       # vel2x
        [-100, 100],       # vel2y
        [-100, 100],       # vel2z
        [-100, 100],       # posx
        [-100, 100],       # posy
        [-100, 100],       # posz
        [0, 1],            # m1
        [0, 1],            # m2
        ]
    }
   
    fileName = f"unprocessed_sobolN{N}.pickle"
    # Load the results
    with open(fileName, 'rb') as handle:
        result = pickle.load(handle)
    
    # Calculate Sobol indices
    output = np.array(result['minDist'])
    S2 = {}
    var_sens = sobol_analyze.analyze(problem, output, calc_second_order=True)
    S1 = var_sens['S1']
    S1_conf = var_sens['S1_conf']
    ST = var_sens['ST']
    ST_conf = var_sens['ST_conf']
    print("First-order Sobol indices:", S1)
    print("Confidence intervals:", S1_conf)
    S2['var'] = pd.DataFrame(var_sens.pop('S2'), index=problem['names'],
                           columns=problem['names'])
    S2['var_conf'] = pd.DataFrame(var_sens.pop('S2_conf'), index=problem['names'],
                           columns=problem['names'])
    print("Second-order Sobol indices:")
    print(S2['var'])
    print("\nConfidence intervals:")
    print(S2['var_conf'])
    var_sens0 = pd.DataFrame(var_sens,index=problem['names'])
    var_sens0 = var_sens0[var_sens0['ST'] >= 0] 

    output = np.array(result['maxDist'])
    S2 = {}
    var_sens = sobol_analyze.analyze(problem, output, calc_second_order=True)
    S1 = var_sens['S1']
    S1_conf = var_sens['S1_conf']
    ST = var_sens['ST']
    ST_conf = var_sens['ST_conf']
    print("First-order Sobol indices:", S1)
    print("Confidence intervals:", S1_conf)
    S2['var'] = pd.DataFrame(var_sens.pop('S2'), index=problem['names'],
                           columns=problem['names'])
    S2['var_conf'] = pd.DataFrame(var_sens.pop('S2_conf'), index=problem['names'],
                           columns=problem['names'])
    print("Second-order Sobol indices:")
    print(S2['var'])
    print("\nConfidence intervals:")
    print(S2['var_conf'])
    var_sens1 = pd.DataFrame(var_sens,index=problem['names'])
    var_sens1 = var_sens1[var_sens1['ST'] >= 0] 
    

    # Make the plot!
    ind = np.arange(len(var_sens0.index))  # the x locations for the groups
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
      
    rects1 = ax.bar(ind - width, var_sens0['ST'], width,
                      yerr=var_sens0['ST_conf'], capsize=4,
                      label='Min Distance between Agents during Sim')
      
    rects2 = ax.bar(ind, var_sens1['ST'], width,
                    yerr=var_sens1['ST_conf'], capsize=4,
                    label='Max Distance between Agents during Sim')
      
    ax.set_ylabel('Total Sobol Index', fontsize=15)
    ax.set_xticks(ind)
    ax.set_xticklabels(( r'$\hat{v}_{1,x}$', r'$\hat{v}_{1,y}$', r'$\hat{v}_{1,z}$',
                         r'$\hat{v}_{2,x}$', r'$\hat{v}_{2,y}$', r'$\hat{v}_{2,z}$',
                         r'$\hat{r}_{2,x}$', r'$\hat{r}_{2,y}$', r'$\hat{r}_{2,z}$',
                         r'$m_1$', r'$m_2$'))
    ubs0 = [var_sens0['ST'].iloc[i] for i in np.arange(len(var_sens0['ST']))]
    ubs1 = [var_sens1['ST'].iloc[i] for i in np.arange(len(var_sens1['ST']))]
    max0 = np.max(ubs0)
    max1 = np.max(ubs1)
    maxVal = np.max([max0, max1])    
    ax.set_ylim(0, 1.1*maxVal)
    ax.legend(fontsize=12)
    imageName = f"sobolN{N}.pdf"
    plt.savefig(imageName)

if __name__ == "__main__":
    args = parser.parse_args()
    if args.mode == 'generate':
        with Pool(args.ncores) as pool:
            main(args.N, args.ncores, pool)
    elif args.mode == 'analyze':
        analyze_sobol(args.N)
    else:
        print('Not a valid mode')
