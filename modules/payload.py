from collections import namedtuple

import numpy as np
from config.config import DEBUG_MODE, coarse_factor, fine_factor
from modules.ansi import *
from modules.user_input import rocket




def rocket_equation(wet_mass, dry_mass, isp):
    # By weight, dV = (isp * g0) * ln(wet mass / dry mass).
    g0 = 9.80665  # m/s^2
    exhaust_velocity = isp * g0
    mass_ratio = wet_mass / dry_mass
    delta_v = exhaust_velocity * np.emath.log(mass_ratio)

    return delta_v


def calculate_total_dv(rocket, payload_mass, breakdown=False, raw=False):
    total_dv = 0
    upper_mass = payload_mass
    stage_dv = []

    if raw:
        wet_mass = rocket.wet_mass
        dry_mass = rocket.dry_mass
    else:
        wet_mass = rocket.wet_mass
        dry_mass = rocket.dry_mass_adj

    for i in reversed(range(rocket.stages)):
        m0 = wet_mass[i] + upper_mass
        m1 = dry_mass[i] + upper_mass
        dv = rocket_equation(m0, m1, rocket.isp[i])

        stage_dv.append(dv)
        total_dv += dv

        upper_mass = m0

    if breakdown:
        return total_dv, stage_dv

    return total_dv


def payload_finder(low_bound, high_bound, step_size, target_dv, rocket):
    PayloadResult = namedtuple("PayloadResult", ["iterations", "payload", "dv"])

    iterations = 0
    best_payload = low_bound
    best_dv = calculate_total_dv(rocket, low_bound)

    if best_dv < target_dv:
        if DEBUG_MODE:
            print("No result possible.")
        return PayloadResult(iterations, best_payload, best_dv)

    payload = low_bound

    while payload <= high_bound:
        dv = calculate_total_dv(rocket, payload)

        if dv >= target_dv:
            best_payload = payload
            best_dv = dv
        else:
            break

        payload += step_size
        iterations += 1

    return PayloadResult(iterations, best_payload, best_dv)


def payload_curve_generator(rocket, step, max_payload, cutoff, raw):
    payloads = []
    dvs = []
    payload = 0.0
    iterations = 0

    while payload <= max_payload:
        dv = calculate_total_dv(rocket, payload, False, raw)
        payloads.append(payload)
        dvs.append(dv)

        if dv <= cutoff:
            break

        payload += step
        iterations += 1

    return payloads, dvs, iterations


def trajectories(rocket, trajectory_targets):
    results = {}

    for name, target_dv in trajectory_targets.items():
        coarse_step = (rocket.rocket_mass / 1000) * coarse_factor  # kg
        fine_step = coarse_step / fine_factor

        coarse = payload_finder(
            low_bound=0,
            high_bound=(0.3 * rocket.rocket_mass),
            step_size=coarse_step,
            target_dv=target_dv,
            rocket=rocket,
        )

        fine_low = max(0, coarse.payload - coarse_step)
        fine_high = coarse.payload + coarse_step

        if DEBUG_MODE:
            print("----------------------------------------")
            print(name)
            print("\nCoarse")
            print(coarse)

        fine = payload_finder(
            low_bound=fine_low,
            high_bound=fine_high,
            step_size=fine_step,
            target_dv=target_dv,
            rocket=rocket,
        )

        if DEBUG_MODE:
            print("\nFine")
            print(fine)
            print("----------------------------------------")

        results[name] = {
            "max_payload": fine.payload,
            "dv": fine.dv,
            "iterations": fine.iterations,
            "target": target_dv,
        }

    print(YELLOW("\n=== Payload Capacity by Target Δv ==="))

    for name, result in results.items():
        print(
            GRAY(
                f"\n  {name:28} ->  {result['max_payload']:9,.2f} kg "
                f"@ Δv {result['dv']:7,.2f} m/s"
            )
        )

        dv, stage_dvs = calculate_total_dv(rocket, result["max_payload"], breakdown=True)
        stages_fmt = [f"Stage {i + 1}: {dv:,.2f} m/s" for i, dv in enumerate(reversed(stage_dvs))]

        for i in range(0, len(stages_fmt), 2):
            print(D_GRAY("     " + " | ".join(stages_fmt[i:i + 2])))

    leo_payload = min(results.values(), key=lambda x: x["target"])["max_payload"]

    return leo_payload
