import matplotlib.pyplot as plt
import numpy as np

from config.config import DEBUG_MODE, DARK_MODE, graph_factor, GRAPH_MODE
from modules.ansi import *
from modules.payload import payload_curve_generator
from matplotlib.widgets import Button


def graph(rocket, leo_payload):
    print(YELLOW("\n=== Rocket Performance ==="))

    rocket_name = rocket.rocket_name

    cutoff = 9200  # m/s. Final graph cutoff; leave this alone as it impacts the integral.
    step = (rocket.rocket_mass / 1000) * graph_factor  # kg
    if GRAPH_MODE == "terminal":
        step = step * 5
    max_payload = rocket.rocket_mass * 0.1  # kg

    payloads, dvs, iterations = payload_curve_generator(
        rocket, step, max_payload, cutoff, False
    )

    # Checking if it is worth plotting the expended graph.
    total_reserve = sum(np.array(rocket.dry_mass_adj) - np.array(rocket.dry_mass))
    reserve_fraction = total_reserve / sum(rocket.dry_mass)
    plot_raw_curve = reserve_fraction > 0.02  # 2% threshold.

    if DEBUG_MODE:
        print(f"Current reserve fraction is: {reserve_fraction}")

    if plot_raw_curve:
        raw_payloads, raw_dvs, raw_iterations = payload_curve_generator(
            rocket, step, max_payload, cutoff, True
        )

    # Numerical calculus calculations for the metrics.
    # Energy cost per payload unit = f'(0) = d(Δv) / d(payload mass).
    # Finite difference differential approximation.
    dv_derivative = []

    for i in range(1, len(dvs)):
        delta_v = dvs[i] - dvs[i - 1]
        delta_payload = payloads[i] - payloads[i - 1]
        slope = (delta_v / delta_payload) if delta_payload != 0 else 0
        dv_derivative.append(slope)

    initial_slope = dv_derivative[0]  # m/s/kg
    normalised_eq = -initial_slope / dvs[0]

    if leo_payload >= 0:
        payload_fraction = leo_payload / rocket.rocket_mass
        leq = -np.log10(normalised_eq / (rocket.rocket_mass * (payload_fraction ** 3)))
    else:
        payload_fraction = 0
        leq = 0
        print("Error finding payload fraction and LEQ")

    # Trapezoidal rule numerical integration.
    area = 0
    for i in range(len(payloads) - 1):
        h = payloads[i + 1] - payloads[i]
        area += 0.5 * (dvs[i] + dvs[i + 1]) * h

    if DEBUG_MODE:
        print(f"Integral: {area:,.3f}")

    heq = area / (rocket.rocket_mass * 100)

    print(f"\n{GRAY('Initial ∆v drop per kg'):<30}: {D_GRAY(f'{initial_slope:.2f} m/s/kg')}")
    print(f"\n{GRAY('LEQ (Low-Energy Quotient)'):<30}: {D_GRAY(f'{leq:.3f}')}")
    print(f"{GRAY('HEQ (High-Energy Quotient)'):<30}: {D_GRAY(f'{heq:.3f}')}")
    print(f"\n{GRAY('Payload Fraction'):<30}: {D_GRAY(f'{payload_fraction * 100:.3f} %')}")
    
        #changing light to dark
    if DARK_MODE:
        plt.style.use("dark_background")
        fig, ax = plt.subplots(figsize=(8, 5), facecolor="black")
        ax.set_facecolor("black")
    else:
        fig, ax = plt.subplots(figsize=(8, 5))

    plt.subplots_adjust(bottom=0.22)

    state = {"mode": "payload"}
    #defining the two graph types
    def draw_payload_graph():
        ax.clear()

        ax.plot(payloads, dvs, "-", lw=2, label="Achieved Δv")

        if plot_raw_curve:
            ax.plot(raw_payloads, raw_dvs, "--", lw=2, label="Achieved Δv without fuel reserves.")
            min_len = min(len(payloads), len(raw_dvs))
            ax.fill_between(
                payloads[:min_len],
                dvs[:min_len],
                raw_dvs[:min_len],
                alpha=0.2,
                label="Performance loss due to reserves",
            )

        if DEBUG_MODE:
            ax.axhline(cutoff, linestyle="--", label=f"Δv cutoff ({cutoff}) m/s")
            ax.axvline(max_payload, linestyle="--", label=f"Payload cutoff: ({max_payload:.1f}) kg")
        elif GRAPH_MODE == "window":
            ax.set_xlim(0, payloads[-1] + 10)
            ax.set_ylim(cutoff - 400, None)

        ax.set_xlabel("Payload mass (kg)")
        ax.set_ylabel("Total Δv (m/s)")
        ax.set_title(f"Rocket Performance: Payload vs. Δv, {rocket_name}")
        ax.grid(True, alpha=0.2 if DARK_MODE else 1)
        if GRAPH_MODE == "window":
            ax.legend(loc="best")
            button.label.set_text("Show derivative")
            fig.canvas.draw_idle()


    def draw_derivative_graph():
        ax.clear()

        ax.plot(payloads[1:], dv_derivative, "-", lw=2, label="d(Δv)/d(payload)")
        

        ax.set_xlabel("Payload mass (kg)")
        ax.set_ylabel("Marginal ∆v loss (m/s per kg payload)")
        ax.set_title(f"Δv Sensitivity to Payload, {rocket_name}")
        ax.grid(True, alpha=0.2 if DARK_MODE else 1)
        if GRAPH_MODE == "window":
            ax.axhline(0, linestyle="--")
            ax.legend(loc="best")
            button.label.set_text("Show payload")
            fig.canvas.draw_idle()

        #defining the toggle
    def toggle_graph(event):
        if state["mode"] == "payload":
            state["mode"] = "derivative"
            draw_derivative_graph()
        else:
            state["mode"] = "payload"
            draw_payload_graph()
    
    #apparently matplotlib has buttons :D
    if GRAPH_MODE == "window":
        button_ax = fig.add_axes([0.36, 0.05, 0.28, 0.075])
        button = Button(button_ax, "Show derivative")
        button.on_clicked(toggle_graph)
        if DARK_MODE:
            button.color = '0.2'
            button.hovercolor = '0.5'

    if GRAPH_MODE == "terminal":
        import plotext as plx
        plx.clear_figure()
        draw_payload_graph()
        print()
        legend = ax.get_legend()
        if legend is not None:
            legend.remove()
        plx.from_matplotlib(fig)
        plx.theme("dark")
        plx.show()  
    
        print()
        plx.clear_figure()
        draw_derivative_graph()
        legend = ax.get_legend()
        if legend is not None:
            legend.remove()        
        plx.from_matplotlib(fig)
        plx.theme("dark")
        plx.show()

    if DEBUG_MODE:
        print(f"Graphing completed with {iterations} iterations.")
    if GRAPH_MODE == "window":
        draw_payload_graph()
        plt.show()





