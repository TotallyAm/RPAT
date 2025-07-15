##############################################
##Rocket Performance Analysis Tool (RPAT) v3##
########## Created by TotallyAm ##############
##############################################


## version 0.5

import matplotlib.pyplot as plt
import numpy as np
from scripts.user_input import getParam

GRAPH = True #whether to run the matplotlib grpahing and subquent experimental analysis - default on
DEBUG_MODE = False #whether to include debugging messages in the log - default off
MAN_STAGE_ADDITION = False #if the mass of subsequent stages has been added to the mass of each stage, do not change

print("----------------------------------------")
print("Rocket Performance Analysis Tool (RPAT)")
print("         Created by TotallyAm")
print("----------------------------------------")

trajectory_targets = {
    "LEO (Low Earth Orbit)       ": 9300,
    "GTO (Geostationary Transfer)": 11800,
    "TLI (Trans-Lunar Injection) ": 12600,
    "Mars Transfer               ": 12900
}

## step factors (more = slower, more accurate)

coarseFactor = 0.01 #factor for the step rate of the coarse calculations (suggest 0.03 at least)
fineFactor   = 40   #factor for the step rate of the fine calculations (suggest 30 at least)

#stage param removed from V5 replaced with user friendly alternative
result = getParam()
if result:
  stages, dryMass, wetMass, isp, manStage = result
  MAN_STAGE_ADDITION = manStage
  if DEBUG_MODE:
   print(f" Manual Stage Addition: {MAN_STAGE_ADDITION}")
else:
  print("Error, please try again")



if MAN_STAGE_ADDITION:
  rocketMass = max(wetMass)
else:
  rocketMass = sum(wetMass)


def rocketEquation(dryMass, wetMass, isp):
  #by weight, dV = (isp * g0) * ln(wet mass/dry mass)
  g0 = 9.80665 #m/s^2
  eV = isp * g0
  massRatio = wetMass/dryMass
  deltaV = eV * np.emath.log(massRatio)
  return deltaV

def calculateTotalDv(dryMass, wetMass, isp, payloadMass, stages):
  totalDv = 0
  upperMass = payloadMass
  #calculates the dV of each stage + payload
  for i in reversed(range(stages)):
    m0 = wetMass[i] + upperMass
    m1 = dryMass[i] + upperMass
    dv = rocketEquation(m1, m0, isp[i])
    totalDv += dv
    if MAN_STAGE_ADDITION == False:
      upperMass = m0
    
  return totalDv



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
    highBound=(2 * wetMass[-1]),
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
  print(f"{name:25} -> max payload {res.payload:9,.2f} kg @ Δv {res.dv:7,.2f} m/s  (in {res.iterations} steps)")
  if(name == "LEO (Low Earth Orbit)       "):
    leoPayload = res.payload


if GRAPH:
  print("Graphing rocket performance......")
  
  cutoff     = 8000 #m/s
  step       = wetMass[-1] * 0.01 #kg
  maxPayload = wetMass[-1] * 1 #kg

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
  
  
  #plotting
  plt.figure(figsize=(8,5))
  plt.plot(payloads, dvs, '-', lw=2, label="Achieved Δv")
  plt.axhline(cutoff, color='red', linestyle='--', label=f"Δv cutoff ({cutoff}) m/s")
  plt.axvline(maxPayload, color='red', linestyle='--', label=f"Payload cutoff: ({maxPayload:.1f}) kg")
  plt.xlabel("Payload mass (kg)")
  plt.ylabel("Total Δv (m/s)")
  plt.title("Rocket Performance: Payload vs. Δv")
  plt.legend(loc='best')
  plt.grid(True)
  plt.tight_layout()
  print(f"Graphing completed with {iterations} iterations.")
  plt.show()

    ########################### Payload Efficiency Analysis ###############################
    # This section estimates the payload efficiency of the launch vehicle by:
    # - Calculating the derivative of Δv with respect to payload mass (d(Δv)/dm)
    # - Normalising the result to produce dimensionless quotients:
    #     - PEQ  = Payload capacity divided by initial Δv sensitivity
    #     - NPEQ = Normalised version using Δv₀
    # This is an experimental feature for theoretical insight and cross-vehicle comparison.
    #######################################################################################


  #Energy cost per payload unit = f'(0) = d(Δv)/d(payload mass)
  dvDerivative = []
  for i in range(1, len(dvs)):
    delta2v = dvs[i] - dvs[i-1]
    deltaP  = payloads[i] - payloads[i-1]
    # Finite difference: rate of ∆v change per unit payload (i.e., d(∆v)/dm)
    slope   = (delta2v / deltaP) if deltaP != 0 else 0
    dvDerivative.append(slope)
  initialSlope = dvDerivative[0] #m/s/kg
  normalisedEq = -initialSlope / dvs[0] #%
  #PEQ = Payload(dv > 9200)/(d(Δv)/d(payload mass(m=0))
  #NPEQ = 1/((d(Δv)/d(payload mass(m=0))/Δv0)

  #d(∆v)/dm = raw payload sensitivity
  #peq = dV resillience vs lifting capacity
  #npeq = dV loss rate scaled to energy
  #mipeq = npeq/2



  dv0 = dvs[0]
  peq  = leoPayload / np.abs(initialSlope)
  npeq = dv0 / np.abs(initialSlope)
  payloadFraction = leoPayload / rocketMass
  print((normalisedEq * payloadFraction), normalisedEq, payloadFraction)
  mipeq = -np.log10((normalisedEq) / (rocketMass * (payloadFraction **(3))))

  print(f"\nInitial ∆v drop per kg: {initialSlope:.2f} m/s/kg")
  print(f"Normalized            : {normalisedEq*100:.4f} % ∆v lost per kg payload (at zero payload)")
  print(f"\nPayload Efficiency Quotient (PEQ)             : {peq:,.0f}")
  print(f"Normalised Payload Efficiency Quotient (NPEQ) : {npeq:,.0f}")
  print(f"Mass independent PEQ (MIPEQ)                  : {mipeq:.3f}")
  print(f"\nPayload Fraction                              : {payloadFraction:.3f} %")


  plt.figure(figsize=(8,5))
  plt.plot(payloads[1:], dvDerivative, '-', lw=2, color='orange', label="d(Δv)/d(payload)")
  plt.xlabel("Payload mass (kg)")
  plt.ylabel("Marginal ∆v loss (m/s per kg payload)")
  plt.title("Δv Sensitivity to Payload")
  plt.axhline(0, color='gray', linestyle='--')
  plt.grid(True)
  plt.legend()
  plt.tight_layout()
  plt.show()

  
  