import time

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp

SCALE = 1000


def solve_cvrp(
    matrix,
    demands,
    nodes,
    capacity,
    num_vehicles,
    depot=0,
    time_limit=10,
    track_progress=False,
):
    n = len(matrix)

    int_matrix = [
        [int(round(matrix[i][j] * SCALE)) for j in range(n)] for i in range(n)
    ]
    demand_list = [demands[nodes[i]] for i in range(n)]

    manager = pywrapcp.RoutingIndexManager(n, num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int_matrix[from_node][to_node]

    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demand_list[from_node]

    demand_idx = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_idx,
        0,
        [capacity] * num_vehicles,
        True,
        "Capacity",
    )

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    params.time_limit.FromSeconds(time_limit)

    progress = []
    if track_progress:

        def on_solution():
            cost = routing.CostVar().Max() / SCALE
            if not progress or cost < progress[-1][1]:
                progress.append((time.perf_counter() - start, cost))

        routing.AddAtSolutionCallback(on_solution)

    start = time.perf_counter()
    solution = routing.SolveWithParameters(params)
    if solution is None:
        return None

    routes = []
    total = 0

    for v in range(num_vehicles):
        index = routing.Start(v)
        route = []
        load = 0

        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            route.append(nodes[node])
            load += demand_list[node]
            next_index = solution.Value(routing.NextVar(index))
            total += routing.GetArcCostForVehicle(index, next_index, v)
            index = next_index

        route.append(nodes[manager.IndexToNode(index)])
        routes.append({"vehicle": v, "nodes": route, "load": load})

    return {"routes": routes, "distance": total / SCALE, "progress": progress}
