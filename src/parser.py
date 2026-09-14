import math


def parse_vrp(path):
    coords = {}
    demands = {}
    capacity = None
    section = None

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("CAPACITY"):
                capacity = int(line.split(":")[1])
                continue

            if line == "NODE_COORD_SECTION":
                section = "coords"
                continue
            if line == "DEMAND_SECTION":
                section = "demands"
                continue
            if line in ("DEPOT_SECTION", "EOF"):
                section = None
                continue

            if section is None:
                continue

            parts = line.split()
            if section == "coords":
                node = int(parts[0])
                coords[node] = (float(parts[1]), float(parts[2]))
            elif section == "demands":
                node = int(parts[0])
                demands[node] = int(parts[1])

    return coords, demands, capacity


def build_distance_matrix(coords, rounded=False):
    """Düğümler arası Öklid (EUC_2D) mesafe matrisini kurar.

    rounded=True ise her mesafe TSPLIB kuralına göre en yakın tam sayıya
    yuvarlanır (nint). Benchmark optimumları (ör. 784) bu kuralla hesaplanır.

    Dönüş:
        matrix -> matrix[i][j] = i. ve j. düğüm arasındaki mesafe
        nodes  -> matris indekslerinin hangi düğüm numarasına karşılık geldiği
                  (ör. nodes[0] == 1 -> matris satır 0, dosyadaki 1 no'lu depo)
    """
    nodes = sorted(coords.keys())
    n = len(nodes)
    matrix = [[0] * n for _ in range(n)]

    for i in range(n):
        for j in range(n):
            xi, yi = coords[nodes[i]]
            xj, yj = coords[nodes[j]]
            d = math.sqrt((xi - xj) ** 2 + (yi - yj) ** 2)
            matrix[i][j] = int(d + 0.5) if rounded else d

    return matrix, nodes
