# Team 5 - Vehicle Routing Problem
# Heuristic solution for VRP using Nearest Neighbor algorithm with vehicle capacity constraints

import matplotlib.pyplot as plt
from math import sqrt

# Step 1: Helper Functions
def distance(c1, c2):
    """Calculate Euclidean distance between two nodes"""
    return sqrt((c1["x"] - c2["x"])**2 + (c1["y"] - c2["y"])**2)

def total_route_distance(route):
    """Calculate total distance for a given route"""
    return sum(distance(customers[route[i]], customers[route[i+1]]) for i in range(len(route)-1))

# Step 2: Read Input File
with open("vrp.txt", "r", encoding="utf-16") as file: 
    lines = [l.strip() for l in file.readlines()]

# Step 3: Initialize Data Structures
customers = {}  # {ID: {x, y, demand, visited}}
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

    # Process coordinates
    if current_section == "coordinates":
        data = line.split()
        if len(data) == 3:
            node_id, x, y = map(int, data)
            customers[node_id] = {"x": x, "y": y, "demand": 0, "visited": False}

    # Process demands
    elif current_section == "demand":
        data = line.split()
        if len(data) == 2:
            node_id, demand = map(int, data)
            if node_id in customers:
                customers[node_id]["demand"] = demand

    # Process depot
    elif current_section == "depot":
        if line.strip() == "-1":
            break
        depot = int(line.strip())

# Step 5: Initialize Vehicles
vehicles = [{"id": i+1, "capacity": vehicle_capacity, "route": []} for i in range(num_vehicles)]

# Step 6: Print Initial Data
print("\nCustomers:")
for customer_id, data in customers.items():
    print(f"ID: {customer_id}, Coordinates: ({data['x']}, {data['y']}), Demand: {data['demand']}, Visited: {data['visited']}")

print("\nVehicles:")
for v in vehicles:
    print(f"ID: {v['id']}, Capacity: {v['capacity']}, Route: {v['route']}")

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
        vehicle["route"].append(next_customer)
        remaining_capacity -= customers[next_customer]["demand"]
        customers[next_customer]["visited"] = True
        unvisited_customers.remove(next_customer)
        current_node = next_customer

    vehicle["route"].append(depot)
    vehicle["capacity"] = remaining_capacity

# Step 8: Handle Unserved Customers (NEW FIX)
remaining_demand = {cid: data["demand"] for cid, data in customers.items() if not data["visited"] and cid != depot}

while remaining_demand:
    for vehicle in sorted(vehicles, key=lambda v: total_route_distance(v["route"])):
        # Reset capacity for new trip (vehicle returns to depot)
        remaining_capacity = vehicle_capacity  
        
        current_node = depot
        route_added = False

        # Prioritize highest demand first
        for cid in sorted(remaining_demand.keys(), key=lambda x: -remaining_demand[x]):
            if remaining_demand[cid] <= remaining_capacity:
                vehicle["route"].extend([current_node, cid, depot])
                remaining_capacity -= remaining_demand[cid]
                customers[cid]["visited"] = True
                del remaining_demand[cid]
                route_added = True
                break  # One customer per additional trip

        if route_added:
            vehicle["capacity"] = remaining_capacity
            print(f"⚡ Vehicle {vehicle['id']} assigned new trip to customer {cid}")
        else:
            continue
    
    else:
        print("\n⚠️ Unserved customers (demand exceeds capacity):", remaining_demand)
        break

# Step 9: Print Final Routes
print("\nGenerated Routes:")
for v in vehicles:
    print(f"Vehicle {v['id']}: Route -> {v['route']}")

# Step 10: Verify All Customers Served
not_visited = [cid for cid, data in customers.items() if not data["visited"] and cid != depot]
if not_visited:
    print("\nUnserved customers:", not_visited)
else:
    print("\n✅ All customers served successfully.")

# Step 11: Calculate Distances
total_distance = 0
print("\n📏 Distance per vehicle:")
for v in vehicles:
    dist = total_route_distance(v["route"])
    total_distance += dist
    print(f"Vehicle {v['id']}: {dist:.2f} units")

print(f"\n🔢 Total distance traveled: {total_distance:.2f} units")

# Step 12: Count Used Vehicles
used_vehicles = [v for v in vehicles if len(v["route"]) > 2]
print(f"\n🚚 Vehicles used: {len(used_vehicles)}/{len(vehicles)}")