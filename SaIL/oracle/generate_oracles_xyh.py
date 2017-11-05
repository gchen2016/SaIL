#!/usr/bin/env python
"""Given as input a list of database folders , we calculate the clairvoyant oracle i.e number of expansions to the goal for each node.
The oracle is then stored in a json file 

Author: Mohak Bhardwaj
Date: October 6, 2017
"""
import argparse
from collections import defaultdict
import json
import pickle
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
sys.path.insert(0, "../../../planning_python")
import time
from planning_python.environment_interface.env_2d import Env2D
from planning_python.state_lattices.common_lattice.xyh_analytic_lattice import XYHAnalyticLattice
from planning_python.cost_functions.cost_function import UnitCost
from planning_python.heuristic_functions.heuristic_function import DubinsHeuristic
from planning_python.data_structures.planning_problem import PlanningProblem
from planning_python.planners.value_iteration import ValueIteration

#Set some environment parameters
x_lims = [0, 201]
y_lims = [0, 201]
start = (0, 0, 0)
goal = (150, 150, np.pi/2.)
turning_radius=2.0
visualize=False

env_params = {'x_lims': x_lims, 'y_lims': y_lims}
lattice_params = {'x_lims': x_lims, 'y_lims': y_lims, 'radius': turning_radius, 'origin': (start[0], start[1]), 'rotation': 0, 'connectivity': 'dubins_turn_90', 'path_resolution': turning_radius/2}
cost_fn = UnitCost() #We want to calculate number of expansions only
heuristic_fn = DubinsHeuristic(turning_radius)
lattice = XYHAnalyticLattice(lattice_params)
lattice.precalc_costs(cost_fn) #Precalculate costs for speedups

planner = ValueIteration()
start_n = lattice.state_to_node(start)
goal_n = lattice.state_to_node(goal)
prob_params = {'heuristic_weight': 0.0} #doesn't matter as    VI will ignore them
prob = PlanningProblem(prob_params)

def get_json_dict(d):
  new_d = dict()
  for key, v in d.iteritems():
    n_k = str(key)
    new_d[n_k] = v
  return new_d

def generate_oracles(database_folders=[], num_envs=1, file_start_num=0, file_type='json'):
  global env_params, lattice_params, cost_fn, heuristic_fn, lattice, planner, start_n, goal_n, prob
     
  e = Env2D()
  print('Generating Oracles')

  for folder in database_folders:
    env_name = os.path.split(os.path.split(os.path.abspath(folder))[0])[1]
    env_folder = os.path.split(os.path.abspath(folder))[1]
    print ("Current Folder: ", folder)
    for i in range(num_envs):
      curr_env_file = os.path.join(os.path.abspath(folder), str(file_start_num + i)+'.png')
      print(curr_env_file)
      e.initialize(curr_env_file, env_params)
      prob.initialize(e, lattice, cost_fn, heuristic_fn, start_n, goal_n, visualize=False)
      planner.initialize(prob) 
      path, path_cost, num_expansions, plan_time, came_from, cost_so_far, c_obs = planner.plan()
      print('Nodes expanded = %d, Time taken = %f'%(num_expansions, plan_time))
      output_file = "oracle_" + str(file_start_num + i) + "." + file_type
      #Write to file
      if file_type == "pickle":
        with open(os.path.join(os.path.abspath("./saved_oracles/xyh/"+env_name+"/"+env_folder), output_file), 'wb') as fh:
          pickle.dump(cost_so_far, fh, protocol = pickle.HIGHEST_PROTOCOL)
      elif file_type == "json":
        with open(os.path.join(os.path.abspath("./saved_oracles/xyh/"+env_name+"/"+env_folder), output_file), 'w') as fh:
          new_cost_so_far = get_json_dict(cost_so_far)
          json.dump(new_cost_so_far, fh, sort_keys=True)
 
      planner.clear_planner()

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('--database_folders', nargs='+', required=True)
  parser.add_argument('--num_envs', type=int)
  parser.add_argument('--file_start_num', type=int)
  parser.add_argument('--file_type', type=str)
  args = parser.parse_args()
  #generate oracles and save results
  generate_oracles(args.database_folders, args.num_envs, args.file_start_num, args.file_type)
  # print(results)