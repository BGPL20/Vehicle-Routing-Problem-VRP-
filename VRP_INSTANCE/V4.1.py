# Team 5 - Vehicle Routing Problem
# Heuristic solution for VRP using Nearest Neighbor algorithm with Vehicle Capacity Constraints and Local Search with 2-opt with Best Improvement

import matplotlib.pyplot as plt
from math import sqrt

# Step 1: Helper Functions
def distance(c1, c2):
    """Calculate Euclidean distance between two nodes"""
    return sqrt((c1["x"] - c2["x"])**2 + (c1["y"] - c2["y"])**2)

def total_route_distance(route):
    """Calculate total distance for a given route"""
    return sum(distance(customers[route[i]], customers[route[i+1]]) for i in range(len(route)-1))

def two_opt_best_improvement(route):
    best = route
    best_distance = total_route_distance(best)
    improved = True

    while improved:
        improved = False
        best_i, best_j = -1, -1
        best_new_route = None
        best_new_distance = best_distance

        for i in range(1, len(best) - 2):
            for j in range(i + 1, len(best) - 1):
                if j - i == 1:
                    continue  # Ignora segmentos consecutivos (sin cambio real)
                new_route = best[:i] + best[i:j][::-1] + best[j:]
                new_distance = total_route_distance(new_route)

                if new_distance < best_new_distance:
                    best_i, best_j = i, j
                    best_new_route = new_route
                    best_new_distance = new_distance
                    improved = True

        if improved:
            best = best_new_route
            best_distance = best_new_distance

    return best

def plot_routes(vehicles, customers, title):
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    plt.figure(figsize=(10, 7))
    for v in vehicles:
        for trip in v["routes"]:
            x = [customers[n]["x"] for n in trip]
            y = [customers[n]["y"] for n in trip]
            color = colors[v["id"] % len(colors)]
            plt.plot(x, y, marker='o', color=color, label=f"Vehicle {v['id']}")
            for i, node in enumerate(trip):
                plt.text(customers[node]["x"], customers[node]["y"], str(node), fontsize=8)
    depot = customers[depot_id]
    plt.scatter(depot["x"], depot["y"], c='black', marker='s', s=100, label='Depot')
    plt.title(title)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.legend()
    plt.grid(True)
    plt.show()

# Step 2: Read Input File
with open("P-n20-k2.txt", "r", encoding="utf-8") as file:
    lines = [l.strip() for l in file.readlines()]

# Step 3: Initialize Data Structures
customers = {}
vehicles = []
vehicle_capacity = 0
depot = None
current_section = None

# Step 4: Parse File Data
for line in lines:
    if "COMMENT" in line and "No of trucks" in line:
        num_vehicles = int(line.split("No of trucks:")[-1].split(",")[0].strip())
    elif "CAPACITY" in line:
        vehicle_capacity = int(line.split(":")[-1].strip())
    elif "NODE_COORD_SECTION" in line:
        current_section = "coordinates"
        continue
    elif "DEMAND_SECTION" in line:
        current_section = "demand"
        continue
    elif "DEPOT_SECTION" in line:
        current_section = "depot"
        continue
    elif "EOF" in line:
        break

    if current_section == "coordinates":
        data = line.split()
        if len(data) == 3:
            node_id, x, y = map(int, data)
            customers[node_id] = {"x": x, "y": y, "demand": 0, "visited": False}
    elif current_section == "demand":
        data = line.split()
        if len(data) == 2:
            node_id, demand = map(int, data)
            if node_id in customers:
                customers[node_id]["demand"] = demand
    elif current_section == "depot":
        if line.strip() == "-1":
            break
        depot = int(line.strip())

# Step 5: Initialize Vehicles
vehicles = [{"id": i+1, "capacity": vehicle_capacity, "routes": []} for i in range(num_vehicles)]
depot_id = depot

# Step 6: Print Initial Data
print("\nCustomers:")
for customer_id, data in customers.items():
    print(f"ID: {customer_id}, Coordinates: ({data['x']}, {data['y']}), Demand: {data['demand']}, Visited: {data['visited']}")

print("\nVehicles:")
for v in vehicles:
    print(f"ID: {v['id']}, Capacity: {v['capacity']}, Routes: {v['routes']}")

print(f"\nDepot: {depot}")
print(f"Number of vehicles: {num_vehicles}")

# Step 7: First Route Assignment (Nearest Neighbor)
unvisited_customers = set(customers.keys())
unvisited_customers.discard(depot)

for vehicle in vehicles:
    remaining_capacity = vehicle["capacity"]
    route = [depot]
    current_node = depot

    while unvisited_customers:
        candidates = [cid for cid in unvisited_customers if customers[cid]["demand"] <= remaining_capacity]
        if not candidates:
            break
        next_customer = min(candidates, key=lambda cid: distance(customers[current_node], customers[cid]))
        route.append(next_customer)
        remaining_capacity -= customers[next_customer]["demand"]
        customers[next_customer]["visited"] = True
        unvisited_customers.remove(next_customer)
        current_node = next_customer

    route.append(depot)
    vehicle["routes"].append(route)

# Step 8: Handle Unserved Customers
remaining_demand = {cid: data["demand"] for cid, data in customers.items() if not data["visited"] and cid != depot}

while remaining_demand:
    for vehicle in sorted(vehicles, key=lambda v: total_route_distance(v["routes"][0] if v["routes"] else [depot])):
        remaining_capacity = vehicle_capacity
        current_node = depot
        route_added = False
        for cid in sorted(remaining_demand.keys(), key=lambda x: -remaining_demand[x]):
            if remaining_demand[cid] <= remaining_capacity:
                new_trip = [depot, cid, depot]
                vehicle["routes"].append(new_trip)
                remaining_capacity -= remaining_demand[cid]
                customers[cid]["visited"] = True
                del remaining_demand[cid]
                route_added = True
                print(f"⚡ Vehicle {vehicle['id']} assigned new trip to customer {cid}")
                break
        if not route_added:
            continue
    else:
        print("\nUnserved customers (demand exceeds capacity):", remaining_demand)
        break

# Step 9: Print Final Routes
print("\n Routes after Nearest Neighbor:\n" + "-"*40)
for v in vehicles:
    print(f"\n Vehicle {v['id']}:")
    for trip_i, trip in enumerate(v["routes"], start=1):
        trip_dist = total_route_distance(trip)
        print(f"  Trip {trip_i}:")
        print(f"    Route : {' → '.join(map(str, trip))}")
        print(f"    Stops : {len(trip) - 2} customers")
        print(f"    Distance: {trip_dist:.2f} units")

total_distance = 0
print("\nDistance per vehicle:")
for v in vehicles:
    for route in v["routes"]:
        dist = total_route_distance(route)
        total_distance += dist
        print(f"Vehicle {v['id']} (trip {v['routes'].index(route)+1}): {dist:.2f} units")

print(f"\nTotal distance traveled: {total_distance:.2f} units")

# Step 10: Visualize Initial Routes
plot_routes(vehicles, customers, "Before 2-opt Optimization")

# Step 11: Local Search Optimization (2-opt Best Improvement)
print("\n Optimizing routes using 2-opt (Best Improvement)...\n" + "-"*50)
for v in vehicles:
    print(f"\n Vehicle {v['id']} optimized routes:")
    for i in range(len(v["routes"])):
        old_route = v["routes"][i]
        optimized_route = two_opt_best_improvement(old_route)
        v["routes"][i] = optimized_route
        dist = total_route_distance(optimized_route)
        print(f"  Trip {i+1}:")
        print(f"    Route   : {' → '.join(map(str, optimized_route))}")
        print(f"    Stops   : {len(optimized_route) - 2} customers")
        print(f"    Distance: {dist:.2f} units")

# Step 12: Visualize Optimized Routes
plot_routes(vehicles, customers, "After 2-opt Optimization")

# Step 13: Verify All Customers Served
not_visited = [cid for cid, data in customers.items() if not data["visited"] and cid != depot]
if not_visited:
    print("\nUnserved customers:", not_visited)
else:
    print("\nAll customers served successfully.")

# Step 14: Calculate Distances
total_distance = 0
print("\nDistance per vehicle:")
for v in vehicles:
    for route in v["routes"]:
        dist = total_route_distance(route)
        total_distance += dist
        print(f"Vehicle {v['id']} (trip {v['routes'].index(route)+1}): {dist:.2f} units")

print(f"\nTotal distance traveled: {total_distance:.2f} units")

# Step 15: Count Used Vehicles
used_vehicles = [v for v in vehicles if len(v["routes"]) > 0]
print(f"\nVehicles used: {len(used_vehicles)}/{len(vehicles)}")