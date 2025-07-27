import json
import os




def loadRockets():
  rockets = {}
  
  #default rockets
  defaultPath = os.path.join(os.path.dirname(__file__), "default_rockets.json")
  with open(defaultPath, "r") as f:
    rockets.update(json.load(f))
  
  #custom rockets
  customPath = os.path.join(os.path.dirname(__file__), "custom_rockets.json")
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

def selectDefault():
  rockets = loadRockets()
  print("\nAvailable Default Rockets:")
  for i, (key, rocket) in enumerate(rockets.items()):
    print(f"{i:3}: {key:2} — {rocket['desc']}")
  selected = input("\nEnter the rocket name or number: ").lower().strip()
  if selected.isdigit():
    index = int(selected)
    if 0 <= index < len(rockets):
      key = list(rockets.keys())[index]
    else:
      print("Invalid selection. Please try again.")
      return None
  elif selected in rockets:
    key = selected
  else:
    print("Rocket not found, please try again.")

  rocket = rockets[key]
  print(f"Selected rocket: {rocket['desc']}")
  return rocket["stages"], rocket["dryMass"], rocket["wetMass"], rocket["isp"], rocket["manStage"], rocket["desc"]
  



def manualEntry():
  while True:
    name = input("What is the name of your rocket? ")
    break
    
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
  
  return stages, dryMass, wetMass, isp, manStage, name


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