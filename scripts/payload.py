import numpy as np
from scripts.ansi import *
from scripts.user_input import rocket
from config import DEBUG_MODE, coarseFactor, fineFactor, graphFactor
  




#finds the dV from mass ratio
def rocketEquation(wetMass, dryMass, isp):
  #by weight, dV = (isp * g0) * ln(wet mass/dry mass)
  g0 = 9.80665 #m/s^2
  eV = isp * g0
  massRatio = wetMass/dryMass
  deltaV = eV * np.emath.log(massRatio)
  return deltaV

#calculates the dV of each stage + payload
def calculateTotalDv(rocket, payloadMass, breakdown=False, raw=False):
  totalDv = 0
  upperMass = payloadMass
  stageDv = []

  if raw:
    wetMass = rocket.wetMass
    dryMass = rocket.dryMass
  else:
    wetMass = rocket.wetMassAdj
    dryMass = rocket.dryMassAdj
  
  for i in reversed(range(rocket.stages)):
    m0 = wetMass[i] + upperMass
    m1 = dryMass[i] + upperMass
    dv = rocketEquation(m0, m1, rocket.isp[i])
    stageDv.append(dv)
    totalDv += dv
    if rocket.man_stage_addition == False:
      upperMass = m0
    
  if breakdown:
    return totalDv, stageDv
  else: return totalDv

## loops calcaulateTotalDv to find the maximum payload mass for the given target dv
def payloadFinder(lowBound, highBound, stepSize, targetDv, rocket):
  from collections import namedtuple
  PayloadResult = namedtuple("PayloadResult", ["iterations", "payload", "dv"])
    
  iterations     = 0
  bestPayload    = lowBound
  bestDv         = calculateTotalDv(rocket, lowBound)
  if(bestDv < targetDv):
    if(DEBUG_MODE):
      print("No result possible.")
    return PayloadResult(iterations, bestPayload, bestDv)
        
  p = lowBound 
  
  while p <= highBound:
   dv = calculateTotalDv(rocket, p)
   
   if dv >= targetDv:
     bestPayload = p
     bestDv  = dv
   else:
     break
   
   p += stepSize
   iterations += 1
  
  return PayloadResult(iterations, bestPayload, bestDv)


## creates an array for a payload graph
def payloadCurveGenerator(rocket, step, maxPayload, cutoff, raw):
  payloads   = [] #x axis
  dvs        = [] #y axis
  p          = 0.0
  iterations = 0

  

  while p <= maxPayload:
    dv = calculateTotalDv(rocket, p, False, raw)
    payloads.append(p)
    dvs.append(dv)
    if dv <= cutoff:
      break
    p += step
    iterations += 1
  
  return payloads, dvs, iterations

def trajectories(rocket, trajectory_targets):
  results = {}

  

  for name, tgtDv in trajectory_targets.items():
  

    coarseStep  = (rocket.rocketMass / 1000 ) * coarseFactor #kg
    fineStep    = coarseStep / fineFactor

    #coarse pass
    coarse = payloadFinder(
      lowBound=0,
      highBound=(0.3 * rocket.rocketMass),
      stepSize=coarseStep,
      targetDv=tgtDv,
      rocket=rocket
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
      rocket=rocket
      )
    if DEBUG_MODE:
      print("\nFine")
      print(fine)
      print("----------------------------------------")

    
    results[name] = {
      "maxPayload"   : fine.payload,
      "dv"        : fine.dv,
      "iterations": fine.iterations,
      "target"    : tgtDv,
  }


  print(YELLOW("\n=== Payload Capacity by Target Δv ==="))


  for name, res in results.items():
    print(GRAY(f"\n  {name:28} ->  {res['maxPayload']:9,.2f} kg "f"@ Δv {res['dv']:7,.2f} m/s"))
    dv, stageDvs = calculateTotalDv(rocket, res['maxPayload'], breakdown=True)
    stages_fmt = [f"Stage {i+1}: {dv:,.2f} m/s" for i, dv in enumerate(reversed(stageDvs))]
    for i in range(0, len(stages_fmt), 2):
        print(D_GRAY("     " + " | ".join(stages_fmt[i:i+2])))


  leoPayload = min(results.values(), key=lambda x: x["target"])["maxPayload"]

  return leoPayload