# RPAT - Rocket Performance Analysis Tool

RPAT is a terminal-based tool for analysing the performance of launch vehicles. It's designed for players of KSP (particularly RP-1), amateur aerospace designers, and anyone who wants a quick, clear look at how well a given rocket performs.

This tool isn't meant to replace detailed simulation or flight testing. Instead, it provides instant feedback on vehicle efficiency, approximate payload capacities, and whether your design actually suits your intended mission.

---

## Purpose and Design Philosophy

RPAT was created to give you information about a rocket, or feedback on your own rocket, without needing to do the tedious calculations for it yourself, then to present them in a clear understandable format.

---

## Features

* **Delta-v vs Payload Graph** - See how added payload affects performance, and see how your rocket behaves at various dVs.
* **Built-in Rocket Presets** - Select from a growing library of default rockets.
* **Efficiency Scores** - Get metrics on how efficient your rocket it at a given role, for comparative use.
* **Payload Finder** - Reports how much payload can be sent to LEO, GTO, or other delta V targets.
* **Custom Vehicle Input** - Simple json system supported for adding your own designs

---

## Installation and Requirements

RPAT requires Python 3 and numpy, it will not work without it. 

RPAT has the ability to generate graphs in two different modes, you can choose between them or disable them in config/config.py, the graphing modes both require matplotlib, but the "terminal" mode also requires plotext.

To quickly install all modules with pip, use:

```bash
pip install numpy matplotlib plotext
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
* **Stage delta-v breakdown** at those limits.
* **Energy quotient scores** to help indicate how effective a rocket actually is, compared to competing designs.

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

<img width="656" height="967" alt="image" src="https://github.com/user-attachments/assets/223b2a8a-81ea-44ac-8d1d-d679bb0684ec" />


---

## Rocket Library

You can select from a library of built-in rockets. When the program runs, you’ll see a list of rockets, such as:

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
* `hypothetical`: For rockets that were designed, but never flown, or for kitbashed rocket components, like a Saturn V with Gem-63s for some reason.

All rockets include a `desc` (description) string for easier identification.

---

## Editing or Adding Rockets

You can edit `custom_rockets.json` to add your own vehicles. Each entry can contain:

```json
  "atlas-v-2x-aj60a": {
    "type"                : "Active",
    "desc"                : "Atlas V with 2 AJ-60A boosters (ULA)",
    "man_stage_add"       : 0,
    "stages"              : 2,
    "dryMass"             : [21054, 2316],
    "wetMass"             : [305143, 3146],
    "isp"                 : [320, 450.5],
    "fuel_reserve": [1000, 0]
   "main_stage_thrust"   : 3827,
    "booster_thrust"      : 1688.4,
    "booster_dry_mass"    : 4067,
    "booster_wet_mass"    : 46697,
    "booster_isp"         : 279.3,
    "booster_count"       : 2,
    "booster_burn_time"   : 94
       
  }
```

Most of these variables should be self explanatory, however a few will need more explanation:

- man_stage_add is a boolean to declare whether the upper stage masses have been added to the lower stages,
for example, adding the wet mass of stage 2 to stage 1. This usually isn't the case, but make sure to declare it if it is.
- fuel_reserve is a list of the fuel you want reserved for each stage, for example if the first stage
lands like in our example above. This does not need to be declared if you don't intend to reserve fuel.
- Booster calculations require all booster fields, in addition they require the core stage thrust.


Use `Rockets.txt` to document your values, assumptions, and sources for transparency.


---

RPAT is under active development, things may change around with updates, but each stable release is tested significantly, and each experimental build is usually checked for mathematically accuracy, if a little buggy overall.
