"""Interactive concept-drift visualiser (V1, diagonal Hamiltonian).

Each concept is a phasor:
    arrow LENGTH = presence     (frozen in V1 -- diagonal H moves no amplitude)
    arrow ANGLE  = relationship (drifts at the concept's own frequency omega)

Drag the slider or hit Play to watch relationships drift while presence stays put.

Self-contained (numpy + matplotlib) so it just runs. The numbers are the same
ones dynamics.QuantumWalk produces for a diagonal H; see state() for how to swap
in the real pipeline.

Run locally:  python visualisation/drift_view.py
"""
from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# name, spin frequency omega, presence (0..1), colour
CONCEPTS = [
    ("aspirin",  4.0, 1.00, "#534AB7"),
    ("headache", 3.0, 0.70, "#D85A30"),
    ("300mg",    3.0, 0.45, "#1D9E75"),
    ("ulcer",    2.0, 0.55, "#E24B4A"),
]
T_MAX = 6.0

NAMES   = [c[0] for c in CONCEPTS]
OMEGA   = np.array([c[1] for c in CONCEPTS])
PRESENT = np.array([c[2] for c in CONCEPTS])
COLORS  = [c[3] for c in CONCEPTS]
PAIRS   = [("aspirin", "ulcer"), ("aspirin", "headache"), ("headache", "300mg")]


def state(t: float) -> np.ndarray:
    """psi_i(t): magnitude = presence (frozen), phase = -omega_i * t.

    Full-pipeline equivalent:
        H    = np.diag(OMEGA).astype(complex)
        psi0 = PRESENT.astype(complex)            # |psi0_i| = presence_i
        psi  = dynamics.QuantumWalk(H).evolve(psi0 / np.linalg.norm(psi0), t)
    """
    return PRESENT * np.exp(-1j * OMEGA * t)


def make_figure():
    times = np.linspace(0, T_MAX, 400)
    ang = np.stack([np.angle(state(t)) for t in times])

    fig, (axp, axd) = plt.subplots(1, 2, figsize=(11, 5))
    plt.subplots_adjust(bottom=0.22)

    axp.add_patch(plt.Circle((0, 0), 1.0, fill=False, color="#bbb", lw=1))
    axp.axhline(0, color="#eee", lw=0.5)
    axp.axvline(0, color="#eee", lw=0.5)
    axp.set_xlim(-1.3, 1.3); axp.set_ylim(-1.3, 1.3); axp.set_aspect("equal")
    axp.set_xticks([]); axp.set_yticks([])
    axp.set_title("concept phasors\nlength = presence  ·  angle = relationship", fontsize=10)

    lines, dots, labels = [], [], []
    for i, name in enumerate(NAMES):
        ln, = axp.plot([0, 0], [0, 0], color=COLORS[i], lw=2.6, solid_capstyle="round")
        dt, = axp.plot([0], [0], "o", color=COLORS[i], ms=6)
        tx = axp.text(0, 0, name, color=COLORS[i], fontsize=10, fontweight="bold", ha="center")
        lines.append(ln); dots.append(dt); labels.append(tx)

    for a, b in PAIRS:
        i, j = NAMES.index(a), NAMES.index(b)
        axd.plot(times, ang[:, i] - ang[:, j], lw=2, label=f"{a} - {b}")
    axd.set_xlabel("evolution time  t"); axd.set_ylabel("relative phase (rad)")
    axd.set_title("relationship drift", fontsize=10)
    axd.grid(alpha=0.25); axd.legend(fontsize=9, loc="lower left")
    vline = axd.axvline(0, color="#666", lw=1)

    def update(t):
        psi = state(t); mag = np.abs(psi); a = np.angle(psi)
        for i in range(len(NAMES)):
            x, y = mag[i] * np.cos(a[i]), mag[i] * np.sin(a[i])
            lines[i].set_data([0, x], [0, y])
            dots[i].set_data([x], [y])
            labels[i].set_position(((mag[i] + 0.14) * np.cos(a[i]), (mag[i] + 0.14) * np.sin(a[i])))
        vline.set_xdata([t, t])
        fig.canvas.draw_idle()

    return fig, update, vline


def main():
    fig, update, _ = make_figure()

    ax_t = plt.axes([0.15, 0.07, 0.55, 0.03])
    slider = Slider(ax_t, "t", 0.0, T_MAX, valinit=0.0)
    slider.on_changed(update)

    ax_b = plt.axes([0.78, 0.055, 0.1, 0.05])
    btn = Button(ax_b, "Play")
    timer = fig.canvas.new_timer(interval=30)
    playing = {"on": False}

    def tick():
        t = slider.val + 0.04
        slider.set_val(0.0 if t > T_MAX else t)

    timer.add_callback(tick)

    def toggle(_evt):
        playing["on"] = not playing["on"]
        btn.label.set_text("Pause" if playing["on"] else "Play")
        (timer.start if playing["on"] else timer.stop)()

    btn.on_clicked(toggle)
    update(0.0)
    plt.show()


if __name__ == "__main__":
    main()