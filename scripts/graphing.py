import matplotlib.pyplot as plt
import numpy as np
import time
from scripts.ansi import *
from scripts.payload import payloadCurveGenerator

from config import DEBUG_MODE, DARK_MODE, graphFactor




def graph(rocket, leoPayload):
  print(YELLOW("\n=== Rocket Performance ==="))
  
  rocketName = rocket.rocketName
  
  cutoff        = 9200 #m/s #final cut off of the graph, leave this alone as it impacts the integral
  step          = (rocket.rocketMass / 1000) * graphFactor #kg
  maxPayload    = rocket.rocketMass * 0.1 #kg


  payloads, dvs, iterations = payloadCurveGenerator(
    rocket, step, maxPayload, cutoff, False
  )


  #checking if it is worth it to plot the expended graph
  totalReserve = sum(np.array(rocket.wetMass) - np.array(rocket.wetMassAdj))
  reserveFraction = totalReserve / sum(rocket.wetMass)
  plot_raw_curve = reserveFraction > 0.02 # 2% threshold

  if DEBUG_MODE:
    print(f"Current reserve fraction is: {reserveFraction}")

  if plot_raw_curve:
    rawPayloads, rawDvs, rawIterations = payloadCurveGenerator(
      rocket, step, maxPayload, cutoff, True
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
    payloadFraction = leoPayload / (rocket.rocketMass)
    LEQ = -np.log10((normalisedEq) / (rocket.rocketMass * (payloadFraction **(3))))
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

  HEQ = (area/(rocket.rocketMass * 100))


  #print quotients
  
  print(f"\n{GRAY('Initial ∆v drop per kg'):<30}: {D_GRAY(f'{initialSlope:.2f} m/s/kg')}")
  print(f"\n{GRAY('LEQ (Low-Energy Quotient)'):<30}: {D_GRAY(f'{LEQ:.3f}')}")
  print(f"{GRAY('HEQ (High-Energy Quotient)'):<30}: {D_GRAY(f'{HEQ:.3f}')}")
  print(f"\n{GRAY('Payload Fraction'):<30}: {D_GRAY(f'{(payloadFraction) * 100:.3f} %')}")
  
  
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
    plt.xlim(0, (payloads[-1] + 10))  
    plt.ylim(cutoff - 400, None)       

  
  plt.xlabel("Payload mass (kg)")
  plt.ylabel("Total Δv (m/s)")
  plt.title(f"Rocket Performance: Payload vs. Δv, {rocketName}")
  plt.legend(loc='best')
  plt.grid(True)
  plt.tight_layout()
  
  
  
  
  
  
  if DEBUG_MODE: 
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
  return