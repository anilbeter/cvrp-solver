import csv
import matplotlib.pyplot as plt

from src.solver import solve_cvrp

OPTIMUM = 784
OPTIMUM_CAPACITY = 100  # 784 sadece bu kapasitede geçerli


def run_case(matrix, demands, nodes, capacity, num_vehicles, time_limit=10):
    result = solve_cvrp(
        matrix, demands, nodes, capacity, num_vehicles, time_limit=time_limit
    )

    row = {
        "capacity": capacity,
        "vehicles": num_vehicles,
        "time_limit": time_limit,
        "distance": None,
        "gap": None,
        "used": 0,
        "max_load": None,
    }

    if result is None:
        return row

    used = sum(1 for r in result["routes"] if len(r["nodes"]) > 2)
    row["distance"] = result["distance"]
    if capacity == OPTIMUM_CAPACITY:
        row["gap"] = (result["distance"] - OPTIMUM) / OPTIMUM * 100
    row["used"] = used
    row["max_load"] = max(r["load"] for r in result["routes"])
    return row


def sweep(
    matrix, demands, nodes, param, values, capacity=100, num_vehicles=5, time_limit=10
):
    rows = []
    for v in values:
        kwargs = {
            "capacity": capacity,
            "num_vehicles": num_vehicles,
            "time_limit": time_limit,
        }
        kwargs[param] = v
        rows.append(run_case(matrix, demands, nodes, **kwargs))
    return rows


def print_table(rows, param):
    header = f"{param:>12} | {'mesafe':>9} | {'fark %':>7} | {'kullanılan':>10} | {'maks yük':>8}"
    print(header)
    print("-" * len(header))
    for r in rows:
        if r["distance"] is None:
            print(f"{r[param]:>12} | {'ÇÖZÜMSÜZ':>9} | {'-':>7} | {'-':>10} | {'-':>8}")
        else:
            gap = "-" if r["gap"] is None else f"{r['gap']:.2f}"
            print(
                f"{r[param]:>12} | {r['distance']:>9.2f} | {gap:>7} | "
                f"{r['used']:>10} | {r['max_load']:>8}"
            )
    print()


def save_csv(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_sweep(rows, param, xlabel, title, path, show_optimum=True):
    valid = [r for r in rows if r["distance"] is not None]
    xs = [r[param] for r in valid]
    ys = [r["distance"] for r in valid]

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.plot(xs, ys, "-o", color="#3498db", linewidth=2)
    ax.set_xticks(xs)
    if show_optimum:
        ax.axhline(
            OPTIMUM,
            color="#e74c3c",
            linestyle="--",
            linewidth=1.2,
            label=f"bilinen optimum ({OPTIMUM})",
        )
        ax.legend(fontsize=8)

    ax.set_xlabel(xlabel)
    ax.set_ylabel("toplam mesafe")
    ax.set_title(title)
    ax.grid(alpha=0.3)

    fig.savefig(path, dpi=150, bbox_inches="tight")
    return fig
