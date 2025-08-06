import json
import os

from scripts.ansi import *
from config import DEFAULT_ROCKETS_PATH, CUSTOM_ROCKETS_PATH

from dataclasses import dataclass
from typing import List

@dataclass
class Rocket:
    name: str
    stages: int
    isp: List[float]
    dryMass: List[float]
    wetMass: List[float]
    dryMassAdj: List[float]
    wetMassAdj: List[float]
    fuel_reserve: List[float]
    man_stage_addition: bool
    rocketName: str
    rocketMass: float

def totalMass(man_stage_addition, wetMass):
  if man_stage_addition:
    rocketMass = max(wetMass)
  else:
    rocketMass = sum(wetMass)
  return rocketMass

def loadRockets():
  rockets = {}
  
  #default rockets
  defaultPath = os.path.join(os.path.dirname(__file__), DEFAULT_ROCKETS_PATH)
  with open(defaultPath, "r") as f:
    rockets.update(json.load(f))
  
  #custom rockets
  customPath = os.path.join(os.path.dirname(__file__), CUSTOM_ROCKETS_PATH)
  if os.path.exists(customPath):
    with open(customPath, "r") as f:
      customPath = json.load(f)
      
      for name, data in customPath.items():
        
        if name in rockets:
          print(f"[Warning] Custom rocket '{name}' conflicts with a default entry and will be skipped.")
          print("To fix this, please rename the rocket to something non-conflicting")
        
        else:
          rockets[name] = data
  
  return rockets


def addReserves(stages, fuel_reserve, dryMass, wetMass):
  dryMassAdj = []
  wetMassAdj = []
  for i in range(stages):
    reserve = fuel_reserve[i]
    prop_mass = wetMass[i] - dryMass[i]
    if reserve > prop_mass:
      print("Fuel reserves are set up incorrectly, resetting")
      reserve = 0
    
    if reserve > 0:
      #print(f"Stage {i + 1} has a fuel reserve of {reserve} kg.")
      dryMassAdj.append(dryMass[i] + reserve)
      wetMassAdj.append(wetMass[i] - reserve)
    
    else:
      dryMassAdj.append(dryMass[i])
      wetMassAdj.append(wetMass[i])
  
  return dryMassAdj, wetMassAdj


def selectDefault():
    rockets = loadRockets()
    print(YELLOW("\nAvailable Default Rockets:"))
    for i, (key, rocket) in enumerate(rockets.items()):
        print(f"{GRAY(f'{i:3}')} : {D_GRAY(key):2} — {GRAY(rocket['desc'])}")
    
    selected = input(f"\n{GREEN('Enter the rocket name or number: ')}").lower().strip()
    
    if selected.isdigit():
        index = int(selected)
        
        if 0 <= index < len(rockets):
            key = list(rockets.keys())[index]
        else:
            print(RED("Invalid selection. Please try again."))
            return None
    
    elif selected in rockets:
        key = selected
    
    else:
        print(RED("Rocket not found, please try again."))
        return None

    rocket = rockets[key]

    fuel_reserve = rocket.get("fuel_reserve", [0] * rocket["stages"])

    dryMassAdj, wetMassAdj = addReserves(rocket["stages"], fuel_reserve, rocket["dryMass"], rocket["wetMass"])

    rocketMass = totalMass(rocket["manStage"], wetMassAdj)

    print(f"{GREEN('Selected rocket:')} {GRAY(rocket['desc'])}")

    return Rocket(
      name=key,
      stages=rocket["stages"],
      isp=rocket["isp"],
      dryMass=rocket["dryMass"],
      wetMass=rocket["wetMass"],
      dryMassAdj=dryMassAdj,
      wetMassAdj=wetMassAdj,
      fuel_reserve=fuel_reserve,
      man_stage_addition=rocket["manStage"],
      rocketName=rocket["desc"],
      rocketMass=rocketMass
    )

  
def manualEntry():
  while True:
    name = input(GREEN("What is the name of your rocket? "))
    break
    
  try:
    stages = int(input(GREEN("How many stages does your rocket have? ")))
  except ValueError: 
    print("Invalid input, please try again.")

  while True:
    response = input(GREEN("Will you be including the mass of the upper stages in the lower stages? (y/n): ")).strip().lower()
    
    if response in ("y", "yes", "true"):
        manStage = True
        break
    
    elif response in ("n", "no", "false"):
        manStage = False
        break
    
    else:
        print(GREEN("Please enter 'y' or 'n'."))
    
    
  dryMass = []
  dryMassAdj = []
  wetMass = []
  wetMassAdj = []
  isp     = []

  for i in range(stages):
    print(YELLOW(f"\nStage {i+1}:"))
    dry  = float(input(GREEN("  Dry mass (kg) : ")))
    wet  = float(input(GREEN("  Wet Mass (kg) : ")))
    isps = float(input(GREEN("  ISP (s)       : ")))
    dryMass.append(dry)
    wetMass.append(wet)
    isp.append(isps)

  fuel_reserve = [0] * stages

  dryMassAdj, wetMassAdj = addReserves(stages, fuel_reserve, dryMass, wetMass)

  rocketMass = totalMass(manStage, wetMassAdj)
  
    
  return Rocket(
      name=name,
      stages=stages,
      isp=isp,
      dryMass=dryMass,
      wetMass=wetMass,
      dryMassAdj=dryMassAdj,
      wetMassAdj=wetMassAdj,
      fuel_reserve=fuel_reserve,
      man_stage_addition=manStage,
      rocketName=name,
      rocketMass=rocketMass
  )



def getParam():
  while True:
    response = input(GREEN("\nDo you want to use a preset rocket? (y/n): ")).strip().lower()
    
    if response in ("y", "yes", "true"):
        return selectDefault()
    
    elif response in ("n", "no", "false"):
        return manualEntry()
    
    else:
        print("Please enter 'y' or 'n'.")
        continue
    
rocket = getParam()