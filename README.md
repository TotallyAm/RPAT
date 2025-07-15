# RPAT — Rocket Performance Analysis Tool

RPAT evaluates the **performance of a launch vehicle**.

It determines the **maximum payload capacity** for a given rocket across target trajectories (LEO, GTO, TLI, etc.) based on a user-defined ∆v cutoff. RPAT also graphs the relationship between **payload mass and delta-v**, giving visual feedback on performance trends, while trying to give you rough idea of how efficiently your rocket is performing based on a series of metrics outlined below.

## Payload Efficiency Metrics

RPAT introduces three key performance quotients that evaluate a launch vehicle's ability to carry payload while minimising delta-v loss:

* **PEQ** quantifies payload capacity relative to early ∆v sensitivity.
* **NPEQ** normalises this against total delta-v.
* **MIPEQ** adds mass and payload scaling for cross-vehicle comparison.

These values are derived automatically from the payload vs ∆v curve and require no manual tuning.

## Visual Derivative Graph

A graph of **∆v loss per kg of payload** helps visualise how performance degrades with increasing payload. This makes it easy to spot whether a rocket is margin-rich or already near its performance ceiling.

## PEQ, NPEQ & MIPEQ: Payload Efficiency Metrics

RPAT calculates three primary efficiency quotients:

* **PEQ (Payload Efficiency Quotient)**
  Defined as the maximum payload the rocket can carry to LEO divided by the initial slope of the ∆v vs. payload curve. This slope, taken at zero payload, represents the rate of delta-v loss per kilogram.

* **NPEQ (Normalised PEQ)**
  Similar in form to PEQ, but instead of using max payload in the numerator, it uses the rocket's initial delta-v (with zero payload). This makes it independent of mission target and better suited for comparing rockets with different total performance levels.

* **MIPEQ (Mass-Independent PEQ)**
  A refined logarithmic score accounting for ∆v sensitivity, vehicle mass, and payload fraction:

  ```
  MIPEQ = -log₁₀( ε / (M × f³) )
  ```

  Where:
  • **ε** = |d(∆v)/dm| ÷ ∆v₀ — the normalised ∆v sensitivity
  • **M** = total wet mass of the rocket
  • **f** = payload fraction (payload mass ÷ total wet mass)

This score is fully normalised and dimensionless, allowing for fair comparisons between vehicles of drastically different sizes and roles.

## How RPAT Calculates These

1. Calculates total ∆v over a range of payloads
2. Computes initial slope (∆v loss per kg)
3. Derives:

   * **PEQ** = Max payload ÷ ∆v loss rate
   * **NPEQ** = Initial ∆v ÷ ∆v loss rate
   * **MIPEQ** = `-log₁₀( (|d(∆v)/dm| / ∆v₀) / (WetMass × PayloadFraction³) )`

| Metric  | Definition               | Insight Gained                             |
| ------- | ------------------------ | ------------------------------------------ |
| `PEQ`   | Max Payload / ∥d(∆v)/dm∥ | Payload per unit ∆v lost                   |
| `NPEQ`  | ∆v₀ / ∥d(∆v)/dm∥         | Payload margin scaled by energy            |
| `MIPEQ` | `-log₁₀( ε / (M × f³) )` | Fully normalised energy–mass–payload score |

## Example Values from LVs:

| Launch Vehicle       | PEQ     | NPEQ   | MIPEQ |
| -------------------- | ------- | ------ | ----- |
| Falcon 9 FT          | 33,192  | 20,982 | 5.997 |
| Electron (Rocketlab) | 23      | 965    | 2.110 |
| Saturn V             | 478,832 | 72,817 | 7.181 |
| Titan II (ICBM)      | 2,782   | 9,680  | 4.147 |



## Installation

To install required dependencies:

```bash
pip install -r requirements.txt
```

To run, simply click one of the .py examples in /Example Scripts or configure RPAT.py with rocket paramaters and run that file. The rest is done automatically.

## Mathematical Methodology

RPAT derives its performance metrics using a simple yet effective numerical differentiation process applied to the delta-v versus payload curve.

1. **Delta-v Calculation**
   For a given payload mass, RPAT computes the total ∆v of the vehicle by summing contributions from each stage using the Tsiolkovsky rocket equation:

   ```
   ∆v = Isp × g₀ × ln(m₀ / m₁)
   ```

   where `m₀` is the initial mass (including payload and upper stages) and `m₁` is the final mass (after propellant is consumed).

2. **∆v vs Payload Graph**
   RPAT generates this curve by evaluating ∆v over a range of payloads. It is sampled iteratively in small steps, and the results are stored as `(payload, ∆v)` data pairs.

3. **Numerical Derivative**
   The rate of ∆v loss per kg of payload (i.e., the slope of the curve) is approximated using finite differences:

   ```
   d(∆v)/dm ≈ (∆v[i+1] - ∆v[i]) / (payload[i+1] - payload[i])
   ```

   The first derivative at zero payload is taken as the initial slope.

4. **Quotients**
   This initial slope value, along with total ∆v and maximum payload, feeds into the three core metrics:

   * **PEQ** = Max payload / |d(∆v)/dm| at payload = 0
   * **NPEQ** = ∆v₀ / |d(∆v)/dm| at payload = 0
   * **MIPEQ** = `-log₁₀( (|d(∆v)/dm| / ∆v₀) / (WetMass × PayloadFraction³) )`

This approach allows RPAT to characterise performance without symbolic calculus or closed-form assumptions — making it well suited for real-world and simulated vehicle configurations.

## Current Limitations

* **Limited presets** - only one rocket is available in the preset, other rockets are available in the precoded /Example Scripts
* **No booster support** but SRBs and strap-on boosters will be implemented later.
* **No crossfeed/asparagus staging** this is unlikely to be supported, but partial modelling via boosters may be possible.
