##############################################
##Rocket Performance Analysis Tool (RPAT) v3##
########## Created by TotallyAm ##############
##############################################

<<<<<<< Updated upstream

## version 0.85 Bingo Fuel

import matplotlib.pyplot as plt
import numpy as np
import json
import os
from scripts.user_input import getParam

GRAPH = True #whether to run the matplotlib grpahing and subquent experimental analysis - default on
DARK_MODE = True
DEBUG_MODE = False #whether to include debugging messages in the log - default off


## step factors (more = slower, more accurate)

coarseFactor = 0.001 #factor for the step rate of the coarse calculations (suggest 0.03 at least)
fineFactor   = 40   #factor for the step rate of the fine calculations (suggest 30 at least)

man_stage_addition = False # leave this alone

print("----------------------------------------")
print("Rocket Performance Analysis Tool (RPAT)")
print("         Created by TotallyAm")
print("----------------------------------------")



#loads the trajectory targets
def loadTargets():
  path = os.path.join(os.path.dirname(__file__), "scripts", "trajectory_targets.json")
  with open(path, "r") as f:
    return json.load(f)

#error checking
try:
  trajectory_targets = loadTargets()
except Exception as e:
    print("[Error] Failed to load trajectory_targets.json:", e)
    trajectory_targets = {} 



#this uses user_inputs.py to find the selected rocket info
result = getParam()
if result:
  stages, dryMass, wetMass, rawDryMass, rawWetMass, isp, manStage, rocketName = result
  man_stage_addition = manStage
  if DEBUG_MODE:
   print(f" Manual Stage Addition: {man_stage_addition}")
else:
  print("Error, please try again")

print(f"\nEvaluating {rocketName}.....")


#this adjusts the definition of rocket mass based on whether the user added the stage masses manually to the first stage
if man_stage_addition:
  rocketMass = max(wetMass)
else:
  rocketMass = sum(wetMass)

#finds the dV from mass ratio
def rocketEquation(dryMass, wetMass, isp):
  #by weight, dV = (isp * g0) * ln(wet mass/dry mass)
  g0 = 9.80665 #m/s^2
  eV = isp * g0
  massRatio = wetMass/dryMass
  deltaV = eV * np.emath.log(massRatio)
  return deltaV

#calculates the dV of each stage + payload
def calculateTotalDv(dryMass, wetMass, isp, payloadMass, stages):
  totalDv = 0
  upperMass = payloadMass
  for i in reversed(range(stages)):
    m0 = wetMass[i] + upperMass
    m1 = dryMass[i] + upperMass
    dv = rocketEquation(m1, m0, isp[i])
    totalDv += dv
    if man_stage_addition == False:
      upperMass = m0
    
  return totalDv
=======

## version 0.90 - MECO


import json
import os
import time
from scripts.user_input import rocket
from scripts.ansi import *
from scripts.payload import trajectories
from scripts.graphing import graph
from config import DEBUG_MODE, GRAPH, TRAJECTORY_TARGETS_PATH


print(D_GRAY("----------------------------------------"))
print(GRAY("Rocket Performance Analysis Tool (RPAT)"))
print(GRAY("         Created by TotallyAm"))
print(D_GRAY("----------------------------------------"))


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
>>>>>>> Stashed changes

## creates an array for a payload graph
def payloadCurveGenerator(dryMass, wetMass, isp, stages, step, maxPayload, cutoff):
  payloads   = [] #x axis
  dvs        = [] #y axis
  p          = 0.0
  iterations = 0

  while p <= maxPayload:
    dv = calculateTotalDv(dryMass, wetMass, isp, p, stages)
    payloads.append(p)
    dvs.append(dv)
    if dv <= cutoff:
      break
    p += step
    iterations += 1
  
  return payloads, dvs, iterations


<<<<<<< Updated upstream
## loops calcaulateTotalDv to find the maximum payload mass for the given target dv
def payloadFinder(lowBound, highBound, stepSize, targetDv, dryMass, wetMass, isp, stages):
  from collections import namedtuple
  PayloadResult = namedtuple("PayloadResult", ["iterations", "payload", "dv"])
    
  iterations     = 0
  bestPayload    = lowBound
  bestDv         = calculateTotalDv(dryMass, wetMass, isp, lowBound, stages)
  if(bestDv < targetDv):
    if(DEBUG_MODE):
      print("No result possible.")
    return PayloadResult(iterations, bestPayload, bestDv)
        
  p = lowBound 
  
  while p <= highBound:
   dv = calculateTotalDv(dryMass, wetMass, isp, p, stages)
   
   if dv >= targetDv:
     bestPayload = p
     bestDv  = dv
   else:
     break
   
   p += stepSize
   iterations += 1
  
  return PayloadResult(iterations, bestPayload, bestDv)


results = {}

for name, tgtDv in trajectory_targets.items():

  coarseStep  = (wetMass[-1]) * coarseFactor #kg
  fineStep    = coarseStep / fineFactor

  #coarse pass
  coarse = payloadFinder(
    lowBound=0,
    highBound=(0.3 * rocketMass),
    stepSize=coarseStep,
    targetDv=tgtDv,
    dryMass=dryMass,
    wetMass=wetMass,
    isp=isp,
    stages=stages
    )
  
  # Set up fine bounds
  fineLow  = max(0, coarse.payload - coarseStep)
  fineHigh = coarse.payload + coarseStep
  if DEBUG_MODE:
    print("----------------------------------------")
    print(name)
    print("\nCoarse")
    print(coarse)
    
  

  # Fine pass
  fine = payloadFinder(
    lowBound=fineLow,
    highBound=fineHigh,
    stepSize=fineStep,
    targetDv=tgtDv,
    dryMass=dryMass,
    wetMass=wetMass,
    isp=isp,
    stages=stages
    )
  if DEBUG_MODE:
    print("\nFine")
    print(fine)
    print("----------------------------------------")

  
  results[name] = fine


print("\n=== Payload Capacity by Target Δv ===")

leoPayload = 0

for name, res in results.items():
  print(f"{name:30} -> max payload {res.payload:9,.2f} kg @ Δv {res.dv:7,.2f} m/s  (in {res.iterations} steps)")
  if(name == "LEO (Low Earth Orbit)"):
    leoPayload = res.payload


if GRAPH:
  print("Graphing rocket performance......")
  
  cutoff        = 9200 #m/s #final cut off of the graph, leave this alone as it impacts the integral
  step          = wetMass[-1] * 0.002 #kg
  maxPayload    = rocketMass * 0.1 #kg


  payloads, dvs, iterations = payloadCurveGenerator(
    dryMass, wetMass, isp, stages, step, maxPayload, cutoff
  )


  #checking if it is worth it to plot the expended graph
  totalReserve = sum(np.array(rawWetMass) - np.array(wetMass))
  reserveFraction = totalReserve / sum(rawWetMass)
  plot_raw_curve = reserveFraction > 0.04  # 2% threshold

  if plot_raw_curve:
    rawPayloads, rawDvs, rawIterations = payloadCurveGenerator(
      rawDryMass, rawWetMass, isp, stages, step, maxPayload, cutoff
    )



  #numerical calculus calculations for the metrics:
   
  #Energy cost per payload unit = f'(0) = d(Δv)/d(payload mass)
  #finite difference differential approximation
  dvDerivative = []
  for i in range(1, len(dvs)):
    delta2v = dvs[i] - dvs[i-1]
    deltaP  = payloads[i] - payloads[i-1]
    # Finite difference: rate of ∆v change per unit payload (i.e., d(∆v)/dm)
    slope   = (delta2v / deltaP) if deltaP != 0 else 0
    dvDerivative.append(slope)
  
  initialSlope = dvDerivative[0] #m/s/kg
  
  normalisedEq = -initialSlope / dvs[0] #%

  if leoPayload >= 0:
    payloadFraction = leoPayload / (rocketMass)
    LEQ = -np.log10((normalisedEq) / (rocketMass * (payloadFraction **(3))))
  else: 
    payloadFraction = 0
    LEQ = 0
    print("Error finding payload fraction and LEQ")

  #trapezoidal rule numerical integration
  area = 0
  for i in range(len(payloads) - 1):
    h = payloads[i+1] - payloads[i]
    area += 0.5 * (dvs[i] + dvs[i+1]) * h
  
  if DEBUG_MODE:
    print(f"Integral: {area:,.3f}")

  HEQ = (area/(rocketMass * 100))


  #print quotients
  
  print(f"\nInitial ∆v drop per kg    : {initialSlope:.2f} m/s/kg")
  print(f"\nLEQ (Low-Energy Quotient) : {LEQ:.3f}")
  print(f"HEQ (High-Energy Quotient): {HEQ:.3f}")
  print(f"\nPayload Fraction          : {(payloadFraction) * 100:.3f} %")
  
  
  #plot for dv = f(payload)
  
  if DARK_MODE:
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(8,5), facecolor='black')
    ax = plt.gca()
    ax.set_facecolor('black')
    plt.grid(color='lightgrey', alpha=0.2)
  else: plt.figure(figsize=(8,5))
  
  
  plt.plot(payloads, dvs, '-', lw=2, label="Achieved Δv")
  
  if plot_raw_curve:
    plt.plot(rawPayloads, rawDvs, '--', lw=2, label="Achieved Δv without fuel reserves.")
    min_len = min(len(payloads), len(rawDvs))
    plt.fill_between(
      payloads[:min_len],
      dvs[:min_len],
      rawDvs[:min_len],
      color='orange', alpha=0.2,
      label="Performance loss due to reserves"
    )
  
  if DEBUG_MODE: 
    plt.axhline(cutoff, color='red', linestyle='--', label=f"Δv cutoff ({cutoff}) m/s")
    plt.axvline(maxPayload, color='red', linestyle='--', label=f"Payload cutoff: ({maxPayload:.1f}) kg")
  else:
    plt.xlim(0, (payloads[-1] + 10))  # x-axis from 0 to your maximum payload
    plt.ylim(cutoff - 400, None)       # y-axis from 0 to auto-detect maximum

  
  plt.xlabel("Payload mass (kg)")
  plt.ylabel("Total Δv (m/s)")
  plt.title(f"Rocket Performance: Payload vs. Δv, {rocketName}")
  plt.legend(loc='best')
  plt.grid(True)
  plt.tight_layout()
  print(f"Graphing completed with {iterations} iterations.")
  plt.show()
  
  
  #plot for d(dv) = f'(payload)
  if DARK_MODE:
     fig = plt.figure(figsize=(8,5), facecolor='black')
     plt.grid(color='lightgrey', alpha=0.2)
  else: plt.figure(figsize=(8,5))
  
  plt.plot(payloads[1:], dvDerivative, '-', lw=2, color='orange', label="d(Δv)/d(payload)")
  plt.xlabel("Payload mass (kg)")
  plt.ylabel("Marginal ∆v loss (m/s per kg payload)")
  plt.title(f"Δv Sensitivity to Payload, {rocketName}")
  plt.axhline(0, color='grey', linestyle='--')
  plt.grid(True)
  plt.legend()
  plt.tight_layout()
  plt.show()
=======


>>>>>>> Stashed changes

  
  