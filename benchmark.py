from src.benchmark import run_instance, print_table, save_progress, plot_progress
from src.sensitivity import save_csv

# küçükten büyüğe, hepsinin optimumu kanıtlanmış (CVRPLIB)
INSTANCES = [
    "A-n32-k5",
    "A-n80-k10",
    "X-n101-k25",
    "X-n200-k36",
    "X-n298-k31",
    "X-n393-k38",
]
TIME_LIMIT = 60
CHECKPOINTS = [1, 10, 30, 60]

rows, progresses = [], []
for name in INSTANCES:
    row, progress = run_instance(name, TIME_LIMIT, CHECKPOINTS)
    rows.append(row)
    progresses.append(progress)
    print(f"{name} tamam (filo {row['fleet']}, fark %{row[f'gap_{TIME_LIMIT}s']:.2f})")

print()
print_table(rows, CHECKPOINTS)
save_csv(rows, "results/benchmark.csv")
save_progress(rows, progresses, "results/benchmark_progress.csv")
plot_progress(rows, progresses, TIME_LIMIT, "results/benchmark_progress.png")

print("Sonuçlar results/benchmark.csv ve results/benchmark_progress.png dosyalarında.")
