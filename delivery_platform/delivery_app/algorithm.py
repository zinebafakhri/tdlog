import os
import requests
import numpy as np
import pandas as pd
import logging

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def get_osrm_route(start, end):
    """
    Fetch the optimal route between two points using OSRM.
    """
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start[1]},{start[0]};{end[1]},{end[0]}"
    response = requests.get(osrm_url, params={"overview": "full", "geometries": "geojson"})
    if response.status_code == 200:
        data = response.json()
        route = data['routes'][0]['geometry']['coordinates']
        # OSRM uses [longitude, latitude], so reverse to [latitude, longitude]
        return [[coord[1], coord[0]] for coord in route]
    else:
        raise ValueError(f"OSRM API error: {response.status_code}")

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth's surface.
    """
    R = 6371  # Earth radius in km
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def optimize_routes_based_on_selection(selected_points):
    """
    Optimize routes based on user-selected delivery points.

    Args:
        selected_points (list): List of [latitude, longitude] pairs.

    Returns:
        list: Optimized routes for each delivery personnel.
    """
    # Predefined starting point
    starting_point = (33.479905, -7.622541)  # Ecole Centrale Casablanca, Bouskoura, Casablanca

    # Validate selected points
    if not all(isinstance(point, list) and len(point) == 2 for point in selected_points):
        raise ValueError("selected_points must be a list of [latitude, longitude] pairs.")

    logger.info(f"Received selected points for optimization: {selected_points}")

    # Split selected points into chunks of 20 for optimization
    selected_points_chunks = [selected_points[i:i + 20] for i in range(0, len(selected_points), 20)]
    all_routes = []

    for chunk in selected_points_chunks:
        # Add starting point to the beginning and end of the route
        chunk = [starting_point] + chunk + [starting_point]

        # Calculate distance matrix
        n = len(chunk)
        dist_matrix = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                dist_matrix[i][j] = haversine(chunk[i][0], chunk[i][1], chunk[j][0], chunk[j][1])

        # Solve TSP using a greedy approach
        visited = [False] * n
        route = [0]  # Start from the starting point
        visited[0] = True

        for _ in range(n - 1):
            last = route[-1]
            next_city = np.argmin([dist_matrix[last][j] if not visited[j] else float('inf') for j in range(n)])
            route.append(next_city)
            visited[next_city] = True

        # Append the starting point to complete the route
        route.append(0)

        # Construct the route using OSRM for visualization
        optimal_route = []
        for i in range(len(route) - 1):
            start = chunk[route[i]]
            end = chunk[route[i + 1]]
            try:
                optimal_route.extend(get_osrm_route(start, end))
            except ValueError as e:
                logger.error(f"Failed to fetch route from {start} to {end}: {str(e)}")
                continue

        all_routes.append(optimal_route)

    logger.info(f"Generated optimized routes: {all_routes}")
    return all_routes