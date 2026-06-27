##############################################
##Rocket Performance Analysis Tool (RPAT) v3##
########## Created by TotallyAm ##############
##############################################


## version 1.0 - Eye Candy!


import json
import os
import time

from modules.ansi import *
from config.config import DEBUG_MODE, GRAPH_MODE, TRAJECTORY_TARGETS_PATH

print(D_GRAY("----------------------------------------"))
print(GRAY("Rocket Performance Analysis Tool (RPAT)"))
print(GRAY("         Created by TotallyAm"))
print(D_GRAY("----------------------------------------"))

from modules.graphing import graph
from modules.payload import trajectories
from modules.user_input import rocket

def load_targets():
    path = os.path.join(os.path.dirname(__file__), TRAJECTORY_TARGETS_PATH)

    with open(path, "r") as file:
        return json.load(file)


try:
    trajectory_targets = load_targets()
except Exception as error:
    print("[Error] Failed to load trajectory_targets.json:", error)
    trajectory_targets = {}


print(GRAY(f"\nEvaluating {rocket.rocket_name}....."))

start_time = time.perf_counter()

leo_payload = trajectories(rocket, trajectory_targets)

if DEBUG_MODE and GRAPH_MODE == "off":
    delta_time = time.perf_counter() - start_time
    print(f"\nThis program took {(delta_time * 1000):.0f} ms to complete.")
elif GRAPH_MODE == "window" or "terminal":
    graph(rocket, leo_payload)

time.sleep(10)
