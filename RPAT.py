##############################################
##Rocket Performance Analysis Tool (RPAT) v3##
########## Created by TotallyAm ##############
##############################################


## version 0.90 - MECO

from scripts.ansi import *
import json
import os
import time

print(D_GRAY("----------------------------------------"))
print(GRAY("Rocket Performance Analysis Tool (RPAT)"))
print(GRAY("         Created by TotallyAm"))
print(D_GRAY("----------------------------------------"))


from scripts.user_input import rocket
from scripts.payload import trajectories
from scripts.graphing import graph
from config import DEBUG_MODE, GRAPH, TRAJECTORY_TARGETS_PATH



#loads the trajectory targets
def loadTargets():
  path = os.path.join(os.path.dirname(__file__), TRAJECTORY_TARGETS_PATH)
  with open(path, "r") as f:
    return json.load(f)

#error checking
try:
  trajectory_targets = loadTargets()
except Exception as e:
    print("[Error] Failed to load trajectory_targets.json:", e)
    trajectory_targets = {} 


print(GRAY(f"\nEvaluating {rocket.rocketName}....."))

startTime = time.perf_counter()


leoPayload = trajectories(rocket, trajectory_targets)

if DEBUG_MODE and not GRAPH:
    deltaTime = time.perf_counter() - startTime
    print(f"\nThis program took {(deltaTime * 1000):.0f} ms to complete.")
elif GRAPH:
  graph(rocket, leoPayload)






  
  