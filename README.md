# RPAT – Rocket Performance Analysis Tool

RPAT is a terminal-based tool for analysing the performance of launch vehicles. It's designed for players of KSP (particularly RP-1), amateur aerospace designers, and anyone who wants a quick, clear look at how well a given rocket performs.

This tool isn't meant to replace detailed simulation or flight testing. Instead, it provides instant feedback on vehicle efficiency, approximate payload capacities, and whether your design actually suits your intended mission.

---

## Purpose and Design Philosophy

RPAT was created to answer a simple question:

> "Is this rocket good at what I built it for?"

The goals were:

* Give clear visual and numerical feedback on a rocket's performance
* Let users compare designs quickly without extra setup
* Remain simple to use, even in a terminal window
* Make the code easy to read, expand, and learn from

It focuses on energy efficiency, payload margins, and practical delta-v capability. It also categorises rockets by role (LEO, deep-space, or general-purpose) based on their energy behaviour.

---

## Features

* **Delta-v vs Payload Graphing** – See how added payload affects performance
* **Built-in Rocket Presets** – Select from a growing library of real and fictional rockets
* **Efficiency Scores** – Get quick insights on whether your vehicle is suited to LEO or high-energy missions
* **Payload Finder** – Reports how much payload can be sent to LEO, GTO, or interplanetary targets
* **Custom Vehicle Input** – Manually enter your own stage data (dry/wet/ISP)
* **Readable Output** – Shows stage breakdown and a summary of what your rocket is good at

---

## Installation and Requirements

RPAT requires Python 3 and the following libraries:

```bash
pip install numpy matplotlib
```

To run it, simply execute the main file:

```bash
python RPAT.py
```

Preset rocket data is stored in `default_rockets.json`. Human-readable explanations for each rocket are provided in `Rockets.txt`.

If you want to add your own preset rockets, `custom_rockets.json` has some examples, you can modify and add your own in here.

---

## How It Works

RPAT uses the Tsiolkovsky rocket equation across each stage to calculate total delta-v. It loops through increasing payload values, recomputing delta-v at each step. This forms the basis of a performance curve: how much delta-v you're left with depending on how much payload you're trying to push.

The tool then derives several values from this curve:

* **Payload limits** for standard mission targets (LEO, GTO, TLI, Mars Transfer)
* **Stage delta-v breakdown** at those limits (planned, not currently available)
* **Energy quotient scores** to classify the rocket's role (prone to occasional tweaks in updates)

---

## Core Metrics

Three key values help summarise a vehicle’s behaviour:

### Low-Energy Quotient (LEQ)

Indicates how well the rocket performs in LEO orbits. High LEQ means it delivers a lot of payload relative to its energy loss when increasing mass. It scales with design efficiency and mass ratio.

### High-Energy Quotient (HEQ)

Derived from the area under the delta-v vs payload curve, then normalised by vehicle mass. High HEQ means the rocket delivers high total impulse and is suited for deep-space or transfer missions.

### Payload Fraction

Simple ratio of payload mass to total launch mass. Gives a general idea of whether a rocket is overbuilt or under-optimised.

---

## Example Output

```text
Initial ∆v drop per kg    : -1.56 m/s/kg

LEQ (Low-Energy Quotient) : 6.270
HEQ (High-Energy Quotient): 5.995

Payload Fraction          : 4.37 %
```

RPAT will also print payload capacities for standard targets like:

* LEO
* GTO
* TLI
* Mars Transfer

---

## Rocket Library

You can select from a library of built-in rockets. When the program runs, you’ll see a list like:

```text
0: falcon9 — Falcon 9 Full Thrust (Expended) (SpaceX)
1: saturnv — Saturn V (NASA, various)
2: dolphinex — Dolphin EX (RP-1)
```

Just enter the number or name to select it.

Each rocket has a `type` tag:

* `active`: In service, real-world vehicle (values may change)
* `historical`: Retired vehicle, values are based on research
* `fictional`: RP-1 rockets or user-made craft, values are exact from RPAT’s context

All rockets include a `desc` (description) string for easier identification.

---

## Editing or Adding Rockets

You can edit `custom_rockets.json` to add your own vehicles. Each entry contains:

```json
{
  "f9": {
  "manStage": 0,
  "stages"  : 2,
  "dryMass" : [22000, 4000],
  "wetMass" : [409000, 111500],
  "isp"     : [311, 348],
  "type"    : "Active",
  "desc"    : "Falcon 9 Block 5 (Drone Ship Landing) (SpaceX)",
  "fuel_reserve" : [38700, 0]
  }
}
```

Most of these variables should be self explanatory, however a few will need more explanation:

- manStage is a boolean to declare whether the upper stage masses have been added to the lower stages,
for example, adding the wet mass of stage 2 to stage 1. This usually isn't the case, but make sure to
declare it if it is.
- fuel_reserve is a list of the fuel you want reserved for each stage, for example if the first stage
lands like in our example above. This does not need to be declared if you don't intend to reserve fuel.


Use `Rockets.txt` to document your values, assumptions, and sources for transparency.

---

## Sample Vehicle Data Table

| Rocket Name                 | Payload to LEO (kg) | LEQ   | HEQ   |
| --------------------------- | ------------------- | ----- | ----- |
| Falcon 9 Block 5 (expended) | 22,773              | 5.918 | 5.198 |
| Delta IV Medium             | 11,329              | 5.392 | 5.352 |
| Saturn V                    | 147,160             | 7.450 | 6.434 |
| N1 (1969)                   | 101,597             | 6.483 | 4.576 |

 This is an example of the output from some of the preset rockets, to be used as a comparison.

---

## Coming Soon / Ideas

* Booster support (SRBs or strap-on side stages) (Coming soon)
* Suborbital calculator (range, apogee, launch angle estimation) (potentially, not confirmed)
* Expanded preset library with more real and RP-1 craft (in progress)
* Automatic performance summaries based on metrics (potentially)
* User inputted fuel reserve system for residual fuel and stage recovery compensation for more accurate figures and to support non-expendable vehicles. (Mostly done)
* A stage-by-stage breakdown of certain trajectories, so you can see at what dV stage separation will occur at for balancing stages properly. (In progress)

---

RPAT is under active development. If you're designing rockets in KSP, RP-1, or in the real world RPAT is a great comparative tool.
