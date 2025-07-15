import json
import os




def loadDefaults():
  path = os.path.join(os.path.dirname(__file__), "rockets.json")
  with open(path, "r") as f:
    return json.load(f)

def selectDefault():
  rockets = loadDefaults()
  print("\nAvailable Default Rockets:")
  for name in rockets: 
    print(f" -{name}")
  
  selected = input("\nEnter the name of a rocket: ").lower().strip()
  if selected in rockets:
    rocket = rockets[selected]
    return rocket["stages"], rocket["dryMass"], rocket["wetMass"], rocket["isp"], rocket["manStage"]
  else:
    print("Rocket not found, please try again.")
    return None

def manualEntry():
  try:
    stages = int(input("How many stages does your rocket have? "))
  except ValueError: 
    print("Invalid input, please try again.")
    
    
  dryMass = []
  wetMass = []
  isp     = []

  for i in range(stages):
    print(f"\nStage {i+1}:")
    dry  = float(input("  Dry mass (kg) : "))
    wet  = float(input("  Wet Mass (kg) : "))
    isps = float(input("  ISP (s)       : "))
    dryMass.append(dry)
    wetMass.append(wet)
    isp.append(isps)

  while True:
    response = input("Did you include the mass of the upper stages in the lower stages? (y/n): ").strip().lower()
    if response in ("y", "yes", "true"):
        manStage = True
        break
    elif response in ("n", "no", "false"):
        manStage = False
        break
    else:
        print("Please enter 'y' or 'n'.")
  
  return stages, dryMass, wetMass, isp, manStage


def getParam():
  while True:
    response = input("Do you want to use a preset rocket? (y/n): ").strip().lower()
    if response in ("y", "yes", "true"):
        return selectDefault()
    elif response in ("n", "no", "false"):
        return manualEntry()
    else:
        print("Please enter 'y' or 'n'.")
        continue