##configs

GRAPH_MODE = "window" #how the graph should be presented ("window", "terminal", "off"), terminal requires plotext module
DARK_MODE  = True
DEBUG_MODE = False #whether to include debugging messages in the log - default off


## step factors

coarse_factor = 0.30  #factor for the step rate of the coarse calculations (suggest between 0.3 and 0.6), lower is more accurate
fine_factor   = 23   #factor for the step rate of the fine calculations (suggest 20 at least) higher is more accurate
graph_factor  = 0.4  #factor for the step rate of the graph (suggest between 0.1 and 0.5)

#shared paths
DEFAULT_ROCKETS_PATH = "../rockets/default_rockets.json"
CUSTOM_ROCKETS_PATH = "../rockets/custom_rockets.json"
TRAJECTORY_TARGETS_PATH = "config/trajectory_targets.json"