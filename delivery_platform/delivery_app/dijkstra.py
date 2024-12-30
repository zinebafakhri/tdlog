import heapq
import math

class Graph:
    def __init__(self):
        self.nodes = {}

    def add_edge(self, from_node, to_node, distance):
        if from_node not in self.nodes:
            self.nodes[from_node] = []
        if to_node not in self.nodes:
            self.nodes[to_node] = []

        self.nodes[from_node].append((to_node, distance))
        self.nodes[to_node].append((from_node, distance))

    def dijkstra(self, start, end):
        queue = [(0, start, [])]
        seen = set()
        min_distances = {start: 0}

        while queue:
            (cost, current_node, path) = heapq.heappop(queue)

            if current_node in seen:
                continue

            seen.add(current_node)
            path = path + [current_node]

            if current_node == end:
                return (cost, path)

            for (neighbor, weight) in self.nodes[current_node]:
                if neighbor in seen:
                    continue

                old_cost = min_distances.get(neighbor, float('inf'))
                new_cost = cost + weight

                if new_cost < old_cost:
                    min_distances[neighbor] = new_cost
                    heapq.heappush(queue, (new_cost, neighbor, path))

        return float('inf'), []

# Example: Creating a graph and calculating the shortest path
road_graph = Graph()

# Example nodes and distances (to be replaced with real data)
road_graph.add_edge("A", "B", 5)
road_graph.add_edge("A", "C", 10)
road_graph.add_edge("B", "C", 2)
road_graph.add_edge("B", "D", 8)
road_graph.add_edge("C", "D", 3)

# Calculate the shortest path using Dijkstra
start_node = "A"
end_node = "D"
cost, path = road_graph.dijkstra(start_node, end_node)
print(f"Shortest path from {start_node} to {end_node}: {path} with cost {cost}")