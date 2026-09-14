from src.parser import parse_vrp, build_distance_matrix
from src.solver import solve_cvrp
from src.plot import plot_routes
from src.sensitivity import sweep, print_table, save_csv, plot_sweep

# 5 araçla optimuma ~7 sn'de, 8 araçla ~20 sn'de ulaşılıyor; 10 sn güvenli değil
TIME_LIMIT = 30

coords, demands, capacity = parse_vrp("data/A-n32-k5.vrp")
matrix, nodes = build_distance_matrix(coords, rounded=True)

# --- Temel çözüm ---
result = solve_cvrp(
    matrix, demands, nodes, capacity, num_vehicles=5, time_limit=TIME_LIMIT
)

for r in result["routes"]:
    print(f"Araç {r['vehicle']}: yük {r['load']:>3} | {r['nodes']}")

print(f"\nToplam mesafe: {result['distance']:.2f}")
print("Bilinen optimum: 784")
print(f"Fark: %{(result['distance'] - 784) / 784 * 100:.2f}\n")

plot_routes(coords, result, path="results/routes_base.png")

# --- Duyarlılık 1: araç sayısı ---
rows_v = sweep(
    matrix,
    demands,
    nodes,
    "num_vehicles",
    [4, 5, 6, 7, 8],
    time_limit=TIME_LIMIT,
)
print_table(rows_v, "vehicles")
save_csv(rows_v, "results/sweep_vehicles.csv")
plot_sweep(
    rows_v,
    "vehicles",
    "araç sayısı",
    "Araç sayısının toplam mesafeye etkisi",
    "results/sweep_vehicles.png",
)

# --- Duyarlılık 2: kapasite ---
rows_c = sweep(
    matrix,
    demands,
    nodes,
    "capacity",
    [100, 120, 140, 160, 200],
    time_limit=TIME_LIMIT,
)
print_table(rows_c, "capacity")
save_csv(rows_c, "results/sweep_capacity.csv")
plot_sweep(
    rows_c,
    "capacity",
    "araç kapasitesi",
    "Kapasitenin toplam mesafeye etkisi",
    "results/sweep_capacity.png",
    show_optimum=False,
)

# --- Duyarlılık 3: çözüm süresi ---
rows_t = sweep(matrix, demands, nodes, "time_limit", [1, 5, 10, 30, 60])
print_table(rows_t, "time_limit")
save_csv(rows_t, "results/sweep_time.csv")
plot_sweep(
    rows_t,
    "time_limit",
    "süre limiti (sn)",
    "Süre limitinin çözüm kalitesine etkisi",
    "results/sweep_time.png",
)

print("Tüm sonuçlar results/ klasörüne kaydedildi.")
