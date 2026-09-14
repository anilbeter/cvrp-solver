import csv
import math

import matplotlib.pyplot as plt

from src.parser import parse_vrp, parse_sol, build_distance_matrix
from src.solver import solve_cvrp

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
LINE = "#2a78d6"


def find_fleet(matrix, demands, nodes, capacity, start):
    # PATH_CHEAPEST_ARC sıkı örneklerde bu filoyla çözüm kuramayınca bütün süreyi
    # harcıyor, o yüzden önce kısa denemelerle filoyu buluyoruz
    fleet = start
    while solve_cvrp(matrix, demands, nodes, capacity, fleet, time_limit=2) is None:
        fleet += 1
    return fleet


def gap_at(progress, t):
    gap = None
    for elapsed, g in progress:
        if elapsed > t:
            break
        gap = g
    return gap


def run_instance(name, time_limit, checkpoints, data_dir="data"):
    coords, demands, capacity = parse_vrp(f"{data_dir}/{name}.vrp")
    bks_routes, optimum = parse_sol(f"{data_dir}/{name}.sol")
    matrix, nodes = build_distance_matrix(coords, rounded=True)

    fleet = find_fleet(matrix, demands, nodes, capacity, len(bks_routes))
    result = solve_cvrp(
        matrix,
        demands,
        nodes,
        capacity,
        fleet,
        time_limit=time_limit,
        track_progress=True,
    )
    progress = [
        (t, (cost - optimum) / optimum * 100) for t, cost in result["progress"]
    ]

    row = {
        "instance": name,
        "customers": len(nodes) - 1,
        "bks_routes": len(bks_routes),
        "fleet": fleet,
        "used": sum(1 for r in result["routes"] if len(r["nodes"]) > 2),
        "optimum": optimum,
        "distance": result["distance"],
    }
    for t in checkpoints:
        row[f"gap_{t}s"] = gap_at(progress, t)
    row["last_improvement"] = progress[-1][0]
    return row, progress


def print_table(rows, checkpoints):
    gap_cols = " | ".join(f"{str(t) + ' sn':>7}" for t in checkpoints)
    header = f"{'örnek':<12} | {'müşteri':>7} | {'filo':>4} | {gap_cols} | {'son iyileşme':>12}"
    print(header)
    print("-" * len(header))
    for r in rows:
        gaps = " | ".join(
            f"{'-':>7}" if r[f"gap_{t}s"] is None else f"{r[f'gap_{t}s']:>7.2f}"
            for t in checkpoints
        )
        print(
            f"{r['instance']:<12} | {r['customers']:>7} | {r['fleet']:>4} | {gaps} | "
            f"{r['last_improvement']:>10.1f} s"
        )
    print()


def save_progress(rows, progresses, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["instance", "time", "gap"])
        for row, progress in zip(rows, progresses):
            for t, g in progress:
                writer.writerow([row["instance"], t, g])


def plot_progress(rows, progresses, time_limit, path):
    cols = 3
    nrows = math.ceil(len(rows) / cols)
    fig, axes = plt.subplots(
        nrows, cols, figsize=(10, 3 * nrows), sharex=True, sharey=True
    )
    fig.patch.set_facecolor(SURFACE)
    top = max(g for p in progresses for _, g in p)

    for ax, row, progress in zip(axes.flat, rows, progresses):
        ts = [t for t, _ in progress] + [time_limit]
        gs = [g for _, g in progress] + [progress[-1][1]]

        ax.set_facecolor(SURFACE)
        ax.step(ts, gs, where="post", color=LINE, linewidth=2, solid_capstyle="round")
        ax.plot(
            ts[-1],
            gs[-1],
            "o",
            color=LINE,
            markersize=8,
            markeredgecolor=SURFACE,
            markeredgewidth=2,
            zorder=3,
            clip_on=False,
        )
        ax.annotate(
            f"%{gs[-1]:.2f}",
            (ts[-1], gs[-1]),
            xytext=(-8, 7),
            textcoords="offset points",
            ha="right",
            color=INK,
            fontsize=9,
        )
        ax.set_title(
            f"{row['instance']} ({row['customers']} müşteri)",
            loc="left",
            color=INK,
            fontsize=10,
        )

        ax.set_xscale("log")
        ax.set_xlim(0.01, time_limit * 1.3)
        ax.set_ylim(0, top * 1.15)
        ax.set_xticks([0.01, 0.1, 1, 10, time_limit])
        ax.set_xticklabels(["0.01", "0.1", "1", "10", str(time_limit)])
        ax.minorticks_off()
        ax.grid(axis="y", color=GRID, linewidth=1)
        ax.set_axisbelow(True)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(BASELINE)
        ax.tick_params(colors=MUTED, labelsize=8, length=0)

    for ax in axes.flat[len(rows):]:
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("süre (sn, log ölçek)", color=MUTED, fontsize=9)
    for ax in axes[:, 0]:
        ax.set_ylabel("optimuma fark (%)", color=MUTED, fontsize=9)

    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    return fig
