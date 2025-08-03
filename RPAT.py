##############################################
##Rocket Performance Analysis Tool (RPAT) v3##
########## Created by TotallyAm ##############
##############################################


## version 0.85 Bingo Fuel

import matplotlib.pyplot as plt
import numpy as np
import json
import os
from scripts.user_input import getParam
from scripts.ansi import *

GRAPH = True #whether to run the matplotlib grpahing and subquent experimental analysis - default on
DARK_MODE = True
DEBUG_MODE = False #whether to include debugging messages in the log - default off



## step factors (more = slower, more accurate)

coarseFactor = 0.001 #factor for the step rate of the coarse calculations (suggest 0.03 at least)
fineFactor   = 40   #factor for the step rate of the fine calculations (suggest 30 at least)

man_stage_addition = False # leave this alone

print(D_GRAY("----------------------------------------"))
print(GRAY("Rocket Performance Analysis Tool (RPAT)"))
print(GRAY("         Created by TotallyAm"))
print(D_GRAY("----------------------------------------"))



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

print(GRAY(f"\nEvaluating {rocketName}....."))


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


print(YELLOW("\n=== Payload Capacity by Target Δv ==="))

leoPayload = 0

for name, res in results.items():
  print(f"{GRAY(name):50} {D_GRAY('-> max payload')} {res.payload:9,.2f} kg @ Δv {res.dv:7,.2f} m/s  {D_GRAY(f'(in {res.iterations} steps)')}")
  if(name == "LEO (Low Earth Orbit)"):
    leoPayload = res.payload


if GRAPH:
  print("\nGraphing rocket performance......")
  
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
  
  print(f"\n{GRAY('Initial ∆v drop per kg'):<30}: {D_GRAY(f'{initialSlope:.2f} m/s/kg')}")
  print(f"{GRAY('LEQ (Low-Energy Quotient)'):<30}: {D_GRAY(f'{LEQ:.3f}')}")
  print(f"{GRAY('HEQ (High-Energy Quotient)'):<30}: {D_GRAY(f'{HEQ:.3f}')}")
  print(f"\n{GRAY('Payload Fraction'):<30}: {D_GRAY(f'{(payloadFraction) * 100:.3f} %')}")
    
    
  #plot for dv = f(payload)
  # Plot 1
  if DARK_MODE:
      plt.style.use('dark_background')
      fig1 = plt.figure(figsize=(8, 5), facecolor='black')
      ax1 = fig1.add_subplot(111)
      ax1.set_facecolor('black')
      ax1.grid(color='lightgrey', alpha=0.2)
  else:
      fig1 = plt.figure(figsize=(8, 5))
      ax1 = fig1.add_subplot(111)

  ax1.plot(payloads, dvs, '-', lw=2, label="Achieved Δv")

  if plot_raw_curve:
      ax1.plot(rawPayloads, rawDvs, '--', lw=2, label="Achieved Δv without fuel reserves.")
      min_len = min(len(payloads), len(rawDvs))
      ax1.fill_between(
          payloads[:min_len],
          dvs[:min_len],
          rawDvs[:min_len],
          color='orange', alpha=0.2,
          label="Performance loss due to reserves"
      )

  if DEBUG_MODE:
      ax1.axhline(cutoff, color='red', linestyle='--', label=f"Δv cutoff ({cutoff}) m/s")
      ax1.axvline(maxPayload, color='red', linestyle='--', label=f"Payload cutoff: ({maxPayload:.1f}) kg")
  else:
      ax1.set_xlim(0, (payloads[-1] + 10))
      ax1.set_ylim(cutoff - 400, None)

  ax1.set_xlabel("Payload mass (kg)")
  ax1.set_ylabel("Total Δv (m/s)")
  ax1.set_title(f"Rocket Performance: Payload vs. Δv, {rocketName}")
  ax1.legend(loc='best')
  ax1.grid(True)
  fig1.tight_layout()

  # Plot 2
  if DARK_MODE:
      fig2 = plt.figure(figsize=(8, 5), facecolor='black')
      ax2 = fig2.add_subplot(111)
      ax2.set_facecolor('black')
      ax2.grid(color='lightgrey', alpha=0.2)
  else:
      fig2 = plt.figure(figsize=(8, 5))
      ax2 = fig2.add_subplot(111)

  ax2.plot(payloads[1:], dvDerivative, '-', lw=2, color='orange', label="d(Δv)/d(payload)")
  ax2.set_xlabel("Payload mass (kg)")
  ax2.set_ylabel("Marginal ∆v loss (m/s per kg payload)")
  ax2.set_title(f"Δv Sensitivity to Payload, {rocketName}")
  ax2.axhline(0, color='grey', linestyle='--')
  ax2.grid(True)
  ax2.legend()
  fig2.tight_layout()

  plt.show()
