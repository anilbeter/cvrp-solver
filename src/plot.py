import matplotlib.pyplot as plt

COLORS = [
    "#e74c3c",
    "#3498db",
    "#2ecc71",
    "#f39c12",
    "#9b59b6",
    "#1abc9c",
    "#e67e22",
    "#34495e",
]


def plot_routes(coords, result, depot_node=1, title=None, path=None):
    fig, ax = plt.subplots(figsize=(9, 8))

    for r in result["routes"]:
        route_nodes = r["nodes"]
        if len(route_nodes) <= 2:
            continue

        xs = [coords[n][0] for n in route_nodes]
        ys = [coords[n][1] for n in route_nodes]
        color = COLORS[r["vehicle"] % len(COLORS)]

        ax.plot(
            xs,
            ys,
            "-o",
            color=color,
            markersize=5,
            linewidth=1.5,
            label=f"Araç {r['vehicle']} (yük {r['load']})",
        )

    for node, (x, y) in coords.items():
        if node == depot_node:
            continue
        ax.annotate(
            str(node), (x, y), fontsize=7, xytext=(3, 3), textcoords="offset points"
        )

    dx, dy = coords[depot_node]
    ax.plot(dx, dy, marker="s", color="black", markersize=12, zorder=5)
    ax.annotate(
        "DEPO",
        (dx, dy),
        fontsize=9,
        fontweight="bold",
        xytext=(6, 6),
        textcoords="offset points",
    )

    ax.set_title(title or f"CVRP çözümü - toplam mesafe {result['distance']:.2f}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.3)

    if path:
        fig.savefig(path, dpi=150, bbox_inches="tight")

    return fig
