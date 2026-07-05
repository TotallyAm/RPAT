import json
import os
from dataclasses import dataclass
from typing import List

from config.config import CUSTOM_ROCKETS_PATH, DEFAULT_ROCKETS_PATH, DEBUG_MODE
from modules.ansi import *
from modules.ansi import USE_ANSI


@dataclass
class Rocket:
    name: str
    stages: int
    isp: List[float]
    dry_mass: List[float]
    wet_mass: List[float]
    dry_mass_adj: List[float]
    fuel_reserve: List[float]
    rocket_name: str
    rocket_mass: float




def load_rockets():
    rockets = {}

    # Default rockets.
    default_path = os.path.join(os.path.dirname(__file__), DEFAULT_ROCKETS_PATH)
    with open(default_path, "r") as file:
        rockets.update(json.load(file))

    # Custom rockets.
    custom_path = os.path.join(os.path.dirname(__file__), CUSTOM_ROCKETS_PATH)
    if os.path.exists(custom_path):
        with open(custom_path, "r") as file:
            custom_rockets = json.load(file)

        for name, data in custom_rockets.items():
            if name in rockets:
                print(RED(f"[Warning] Custom rocket '{name}' conflicts with a default entry and will be skipped."))
                print(GREEN("To fix this, please rename the rocket to something non-conflicting"))
            else:
                rockets[name] = data

    return rockets


def group_rockets(rockets):
    grouped = {}

    for key, rocket_data in rockets.items():
        rocket_type = rocket_data.get("type", "Uncategorised")
        family = rocket_data.get("family", rocket_data.get("desc", key))
        variant = rocket_data.get("variant", rocket_data.get("desc", key))

        grouped.setdefault(rocket_type, {})
        grouped[rocket_type].setdefault(family, [])
        grouped[rocket_type][family].append((variant, key, rocket_data))
    
    return grouped


def choose_from_menu(title, options, label_func=str, skip_single=True, allow_back=True, page_size=7):
    if skip_single and len(options) == 1:
        return options[0]


    def clear_previous_lines(line_count):
        if USE_ANSI:
            for _ in range(line_count):
                print("\033[1A\033[2K", end="")
                print("\r", end="")
        else:
            os.system("cls" if os.name == "nt" else "clear")
    
    page = 0

    while True:
        total_pages = max(1, (len(options) + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))

        start = page * page_size
        end = start + page_size
        page_options = options[start:end]

        
        current_lines_printed = 0

        print(YELLOW(f"\n{title}"))
        print(GRAY(f"Page {page + 1}/{total_pages}\n"))
        current_lines_printed += 4

        if allow_back:
            print(f"{GRAY('0')} : {D_GRAY('Back')}")
            current_lines_printed += 1

        for i, option in enumerate(page_options, start=1):
            print(f"{GRAY(str(i))} : {GRAY(label_func(option))}")
            current_lines_printed += 1

        if total_pages > 1:
            print()
            print(f"{GRAY('8')} : {D_GRAY('Previous page')}")
            print(f"{GRAY('9')} : {D_GRAY('Next page')}")
            lines_printed += 3

        selected = input(f"\n{GREEN('Select option: ')}").strip()
        current_lines_printed += 2



        if selected == "0" and allow_back:
            clear_previous_lines(current_lines_printed)
            return "BACK"

        if selected == "8" and total_pages > 1:
            page -= 1
            continue

        if selected == "9" and total_pages > 1:
            page += 1
            continue

        if not selected.isdigit():
            clear_previous_lines(current_lines_printed)
            continue

        index = int(selected) - 1

        if 0 <= index < len(page_options):
            clear_previous_lines(current_lines_printed)
            return page_options[index]

def select_rocket_key(rockets):
    grouped = group_rockets(rockets)

    while True:
        rocket_type = choose_from_menu(
            "Rocket Types",
            sorted(grouped.keys()),
            skip_single=False,
            allow_back=False,
        )

        if rocket_type is None:
            return None

        while True:
            family = choose_from_menu(
                f"{rocket_type} Families",
                sorted(grouped[rocket_type].keys()),
                skip_single=False
            )

            if family == "BACK":
                break

            while True:
                variant = choose_from_menu(
                    f"{family} Variants",
                    grouped[rocket_type][family],
                    label_func=lambda item: item[0],
                )

                if variant == "BACK":
                    break

                _, key, _ = variant
                return key
    
def rocket_display_name(key, rocket_data):
    if "family" in rocket_data and "variant" in rocket_data:
        return f"{rocket_data['family']} {rocket_data['variant']}"

    return rocket_data.get("desc", key)

def isolate_stage_masses(dry_mass, wet_mass):
    isolated_dry = []
    isolated_wet = []

    for i in range(len(wet_mass) - 1):
        isolated_wet.append(wet_mass[i] - wet_mass[i + 1])
        isolated_dry.append(dry_mass[i] - wet_mass[i + 1])

    isolated_wet.append(wet_mass[-1])
    isolated_dry.append(dry_mass[-1])

    return isolated_dry, isolated_wet


def add_reserves(stages, fuel_reserve, dry_mass, wet_mass):
    dry_mass_adj = []

    for i in range(stages):
        reserve = fuel_reserve[i]
        prop_mass = wet_mass[i] - dry_mass[i]

        if reserve > prop_mass:
            print(RED("Fuel reserves are set up incorrectly, resetting"))
            reserve = 0

        if reserve > 0:
            dry_mass_adj.append(dry_mass[i] + reserve)
        else:
            dry_mass_adj.append(dry_mass[i])

    return dry_mass_adj

def booster_stage_calc(booster_dry_mass, booster_wet_mass, booster_count, booster_thrust, 
                       booster_isp, main_stage_thrust, main_stage_isp, wet_mass, dry_mass, booster_burn_time):
    
    booster_dry_sum = booster_dry_mass * booster_count
    booster_wet_sum = booster_wet_mass * booster_count
    booster_thrust_sum = booster_thrust * booster_count

    #average the ISP weighted by the thrust of each component to get the effective ISP of the combined system
    effective_isp = (booster_thrust_sum + main_stage_thrust) / ((main_stage_thrust / main_stage_isp) + (booster_thrust_sum / booster_isp))
    
    g0 = 9.80665 #m/s^2
    core_mass_flow = (main_stage_thrust * 1000) / (main_stage_isp * g0) #json data is in kN, so multiply by 1000 to get N
    core_mass_used = core_mass_flow * booster_burn_time  

    booster_stage_wet = booster_wet_sum + core_mass_used
    booster_stage_dry = booster_dry_sum
    
    core_stage_wet = wet_mass[0] - core_mass_used
    core_stage_dry = dry_mass[0]

    core_prop_available = wet_mass[0] - dry_mass[0]

    if core_mass_used >= core_prop_available:
        raise ValueError("Booster burn consumes all first-stage core propellant.")

    if DEBUG_MODE:
        print(YELLOW("Booster Stage Calculation:\n"))
        print(f"Effective ISP: {effective_isp:.2f}s\n")
        print(f"Booster Dry Mass: {booster_dry_mass:.2f} kg")
        print(f"Booster Wet Mass: {booster_wet_mass:.2f} kg\n")
        print(f"Booster Count: {booster_count}")
        print(f"Booster Dry Mass Sum: {booster_dry_sum:.2f} kg")
        print(f"Booster Wet Mass Sum: {booster_wet_sum:.2f} kg\n")
        print(f"Core Mass Flow: {core_mass_flow:.2f} kg/s")
        print(f"Core Mass Used: {core_mass_used:.2f} kg\n")
        print(f"Booster Stage Wet Mass: {booster_stage_wet:.2f} kg")
        print(f"Booster Stage Dry Mass: {booster_stage_dry:.2f} kg\n")
        print(f"Core Stage Wet Mass: {core_stage_wet:.2f} kg")
        print(f"Core Stage Dry Mass: {core_stage_dry:.2f} kg\n")

    return effective_isp, booster_stage_wet, booster_stage_dry, core_stage_wet, core_stage_dry

def apply_booster_stage(
    stages, isp, dry_mass_adj, dry_mass, wet_mass, fuel_reserve,
    booster_dry_mass, booster_wet_mass, booster_count, booster_thrust,
    booster_isp, booster_burn_time, main_stage_thrust,
):
    if DEBUG_MODE:
        print(YELLOW("Booster application results:\n"))
        print(f"Previous wet masses: {[round(elem, 2) for elem in wet_mass]} kg")
        print(f"Previous dry masses: {[round(elem, 2) for elem in dry_mass_adj]} kg")
        print(f"Previous ISPs: {[round(elem, 2) for elem in isp]}s\n")
    
    effective_isp, booster_stage_wet, booster_stage_dry, core_stage_wet, core_stage_dry = booster_stage_calc(
        booster_dry_mass, booster_wet_mass, booster_count,
        booster_thrust, booster_isp, main_stage_thrust,
        isp[0], wet_mass, dry_mass, booster_burn_time,
    )


    return {
        "stages": stages + 1,
        "isp": [effective_isp, *isp],
        "dry_mass": [booster_stage_dry, core_stage_dry, *dry_mass[1:]],
        "dry_mass_adj": [booster_stage_dry, dry_mass_adj[0], *dry_mass_adj[1:]],    
        "wet_mass": [booster_stage_wet, core_stage_wet, *wet_mass[1:]],
        "fuel_reserve": [0, *fuel_reserve],
        
    }


def select_default():
    rockets = load_rockets()
    key = select_rocket_key(rockets)
    if key is None:
        return None

    rocket_data = rockets[key]
   
    isp = rocket_data["isp"]  

    manual_stage_addition = rocket_data.get("manStage", rocket_data.get("man_stage_add", False))
    
    dry_mass = rocket_data.get("dryMass", rocket_data.get("dry_mass", 0))
    wet_mass = rocket_data.get("wetMass", rocket_data.get("wet_mass", 0))

    if len(dry_mass) != len(wet_mass) and len(wet_mass) and len(rocket_data["isp"]):
        print(RED("Staging mismatch detected, check your staging!"))
    
    stages = len(dry_mass)
    fuel_reserve = rocket_data.get("fuel_reserve", [0] * stages)
    

        

    if manual_stage_addition:
        dry_mass, wet_mass = isolate_stage_masses(dry_mass, wet_mass)
        if DEBUG_MODE:
            print("Manual stage addition is enabled, adjusting dry and wet masses accordingly.\n")
            print(f"Previous dry masses: {rocket_data.get('dryMass', rocket_data.get('dry_mass', 0))} kg")
            print(f"Previous wet masses: {rocket_data.get('wetMass', rocket_data.get('wet_mass', 0))} kg\n")
            print(f"Adjusted dry masses: {dry_mass} kg")
            print(f"Adjusted wet masses: {wet_mass} kg\n")

    dry_mass_adj = add_reserves(stages, fuel_reserve, dry_mass, wet_mass, )
    
    rocket_mass = sum(wet_mass)  # Total wet mass of the rocket.
    
    boosters = rocket_data.get("boosters", {})
    booster_count = boosters.get("count", 0)
    if booster_count > 0:
        required_booster_fields = [
            "dry_mass",
            "wet_mass",
            "isp",
            "burn_time",
            "thrust",
        ]

        missing_fields = [
            field for field in required_booster_fields
            if field not in boosters
        ]

        if missing_fields:
            print(RED(f"Invalid booster data. Missing: {', '.join(missing_fields)}"))
            return None

        booster_result = apply_booster_stage(
            stages, isp, dry_mass_adj, dry_mass,
            wet_mass, fuel_reserve,
            boosters["dry_mass"],
            boosters["wet_mass"],
            booster_count,
            boosters["thrust"],
            boosters["isp"],
            boosters["burn_time"],
            rocket_data["main_stage_thrust"],
)

        stages = booster_result["stages"]
        isp = booster_result["isp"]
        dry_mass = booster_result["dry_mass"]
        dry_mass_adj = booster_result["dry_mass_adj"]
        wet_mass = booster_result["wet_mass"]
        fuel_reserve = booster_result["fuel_reserve"]
        rocket_mass = rocket_mass + boosters["wet_mass"] * booster_count

        if DEBUG_MODE:
            print(f"Updated ISPs: {[round(elem, 2) for elem in isp]}s")
            print(f"Updated wet masses: {[round(elem, 2) for elem in wet_mass]} kg")
            print(f"Updated dry masses: {[round(elem, 2) for elem in dry_mass_adj]} kg\n")



    print(f"{GREEN('Selected rocket:')} {GRAY(rocket_display_name(key, rocket_data))}")

    return Rocket(
        name=key,
        stages=stages,
        isp=isp,
        dry_mass=dry_mass,
        wet_mass=wet_mass,
        dry_mass_adj=dry_mass_adj,
        fuel_reserve=fuel_reserve,
        rocket_name=rocket_display_name(key, rocket_data),
        rocket_mass=rocket_mass,
    )


rocket = select_default()