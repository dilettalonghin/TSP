import pandas as pd
import numpy as np
from deap import base, creator, tools, algorithms
import random
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from adjustText import adjust_text
from deap.tools import hypervolume
from deap.tools._hypervolume import hv

# Function to load and process CSV files
def load_and_process_file(file_path):
    df = pd.read_csv(file_path, delimiter=',', na_values="-")
    df = df.fillna(float('inf'))
    df = df.set_index(df.columns[0])
    return df

def sort_matrix(matrix, num_cities):
    # Sort the first num_cities in alphabetical order
    cities = sorted(matrix.index)[:num_cities]
    sorted_matrix = matrix.loc[cities, cities]
    return sorted_matrix

def combine_matrices_time(time_bus, time_train, time_plane, num_cities):
    sorted_time_bus = sort_matrix(time_bus, num_cities)
    sorted_time_train = sort_matrix(time_train, num_cities)
    sorted_time_plane = sort_matrix(time_plane, num_cities)
    
    # Combine the matrices
    combined_time_matrix = pd.DataFrame(index=sorted_time_bus.index, columns=sorted_time_bus.columns)
    transport_time_matrix = pd.DataFrame(index=sorted_time_bus.index, columns=sorted_time_bus.columns)
    for i in sorted_time_bus.index:
        for j in sorted_time_bus.columns:
            times = {'bus': sorted_time_bus.loc[i, j], 'train': sorted_time_train.loc[i, j], 'plane': sorted_time_plane.loc[i, j]}
            min_time_transport = min(times, key=times.get)
            min_time = times[min_time_transport]
            if min_time == float('inf'):
                combined_time_matrix.loc[i, j] = float('inf')
                transport_time_matrix.loc[i, j] = None
            else:
                combined_time_matrix.loc[i, j] = min_time
                transport_time_matrix.loc[i, j] = min_time_transport
                
    return combined_time_matrix, transport_time_matrix

def combine_matrices_cost(cost_bus, cost_train, cost_plane, num_cities):
    sorted_cost_bus = sort_matrix(cost_bus, num_cities)
    sorted_cost_train = sort_matrix(cost_train, num_cities)
    sorted_cost_plane = sort_matrix(cost_plane, num_cities)
    
    # Combine the matrices
    combined_cost_matrix = pd.DataFrame(index=sorted_cost_bus.index, columns=sorted_cost_bus.columns)
    transport_cost_matrix = pd.DataFrame(index=sorted_cost_bus.index, columns=sorted_cost_bus.columns)
    for i in sorted_cost_bus.index:
        for j in sorted_cost_bus.columns:
            costs = {'bus': sorted_cost_bus.loc[i, j], 'train': sorted_cost_train.loc[i, j], 'plane': sorted_cost_plane.loc[i, j]}
            min_cost_transport = min(costs, key=costs.get)
            min_cost = costs[min_cost_transport]
            if min_cost == float('inf'):
                combined_cost_matrix.loc[i, j] = float('inf')
                transport_cost_matrix.loc[i, j] = None
            else:
                combined_cost_matrix.loc[i, j] = min_cost
                transport_cost_matrix.loc[i, j] = min_cost_transport
                
    return combined_cost_matrix, transport_cost_matrix

def plot_path(individual, filtered_matrix, coordinates, transport_matrix):
    cities = filtered_matrix.index
    path = [cities[i] for i in individual] + [cities[individual[0]]]
    #print(f'Best path: {path}')

    # Extracting latitudes and longitudes
    lats = [coordinates.loc[city, 'Latitude'] for city in path]
    longs = [coordinates.loc[city, 'Longitude'] for city in path]

    # Create a GeoDataFrame for the path
    path_df = pd.DataFrame({'City': path, 'Latitude': lats, 'Longitude': longs})
    geometry = [Point(xy) for xy in zip(path_df['Longitude'], path_df['Latitude'])]
    geo_df = gpd.GeoDataFrame(path_df, geometry=geometry)

    # Set the coordinate reference system
    geo_df = geo_df.set_crs(epsg=4326)
    geo_df = geo_df.to_crs(epsg=3857)

    # Create the plot
    fig, ax = plt.subplots(figsize=(15, 10))

    # Plot the cities
    geo_df.plot(ax=ax, markersize=20, color='red', marker='o', label='Cities')

    # Mark the starting city with a thick orange cross
    start_city = geo_df.iloc[0]
    ax.plot(start_city.geometry.x, start_city.geometry.y, 'x', color='orange', markersize=10, markeredgewidth=3, label='Start City')

    # Define colors for different transports
    transport_colors = {'bus': 'blue', 'train': 'green', 'plane': 'red'}

    # Plot the path with arrows
    for i in range(len(geo_df) - 1):
        start = geo_df.iloc[i].geometry
        end = geo_df.iloc[i + 1].geometry
        transport = transport_matrix.iloc[individual[i], individual[(i + 1) % len(individual)]]
        color = transport_colors.get(transport, 'black')
        ax.annotate('', xy=(end.x, end.y), xytext=(start.x, start.y),
                    arrowprops=dict(arrowstyle='->', color=color, lw=2))

    # Add labels for each city
    texts = []
    for x, y, label in zip(geo_df.geometry.x, geo_df.geometry.y, geo_df['City']):
        texts.append(ax.text(x, y, label, fontsize=8, ha='right'))

    # Set fixed plot limits to cover the entire map of Europe
    ax.set_xlim(-3000000, 4000000)
    ax.set_ylim(4000000, 10500000)

    # Add basemap with contextily and set the zoom level
    ctx.add_basemap(ax, crs=geo_df.crs.to_string(), source=ctx.providers.CartoDB.PositronNoLabels, zoom=4)

    # Adjust text to avoid overlap
    adjust_text(texts, 
                only_move={'points': 'xy', 'texts': 'xy'},  # Allow movement in both x and y directions
                arrowprops=dict(arrowstyle='-', color='gray', lw=0.5, shrinkA=5, shrinkB=5),
                expand_text=(1.2, 1.4),  # Expand the space around the text
                expand_points=(1.2, 1.4),  # Expand the space around the points
                force_text=1.0,  # Increase the force to separate text
                force_points=1.0)  # Increase the force to separate points

    # Add legend
    handles = [plt.Line2D([0], [0], color=color, lw=2) for color in transport_colors.values()]
    handles.append(plt.Line2D([0], [0], color='orange', marker='x', markersize=10, markeredgewidth=3, linestyle='None'))
    labels = list(transport_colors.keys()) + ['Start City']
    ax.legend(handles, labels, title='Transport')

    # Set the title and axis labels
    plt.title('Best Path on the Map of Europe')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    # Show the plot
    plt.grid(True)
    plt.show()

def custom_heuristic(combined_time_matrix, coordinates):
    # Filter coordinates to include only cities present in the filtered_matrix
    filtered_coordinates = coordinates.loc[combined_time_matrix.index]
    
    # Divide cities into bottom half and top half
    median_y = filtered_coordinates['Latitude'].median()
    #print(f"Median latitude: {median_y}")  # Print the median latitude
    
    bottom_half = filtered_coordinates[filtered_coordinates['Latitude'] <= median_y]
    top_half = filtered_coordinates[filtered_coordinates['Latitude'] > median_y]
    
    # Sort bottom half by X ascending
    bottom_half_sorted = bottom_half.sort_values(by='Longitude', ascending=True)
    
    # Sort top half by X descending
    top_half_sorted = top_half.sort_values(by='Longitude', ascending=False)
    
    # Initialize the tour list
    tour = []
    
    # Add cities from the bottom half to the tour
    for city in bottom_half_sorted.index:
        tour.append(city)
    
    # Add cities from the top half to the tour
    for city in top_half_sorted.index:
        tour.append(city)
    
    # Convert city names to indices
    tour_indices = [combined_time_matrix.index.get_loc(city) for city in tour]
    #print(f"Custom heuristic tour: {tour_indices}")
    
    return tour_indices

# Evaluation function for the multi-objective TSP
def evalTSPMulti(individual, combined_cost_matrix, combined_time_matrix):
    total_cost = 0
    total_time = 0

    for i in range(len(individual) - 1):
        cost = combined_cost_matrix.iloc[individual[i], individual[i + 1]]
        time = combined_time_matrix.iloc[individual[i], individual[i + 1]]
        
        if cost == float('inf') or time == float('inf'):
            total_cost += 10000000  # Apply a large penalty for infeasible connections
            total_time += 10000000  # Apply a large penalty for infeasible connections
        else:
            total_cost += cost
            total_time += time

    # Add the cost and time to return to the starting city
    cost = combined_cost_matrix.iloc[individual[-1], individual[0]]
    time = combined_time_matrix.iloc[individual[-1], individual[0]]
    
    if cost == float('inf') or time == float('inf'):
        total_cost += 10000000  # Apply a large penalty for infeasible connections
        total_time += 10000000  # Apply a large penalty for infeasible connections
    else:
        total_cost += cost
        total_time += time

    return total_cost, total_time

# DEAP configuration
creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selNSGA2)
toolbox.register("evaluate", evalTSPMulti)

# Main function to run NSGA-II
def main(num_cities, use_heuristic):
    
    # Load cost and time matrices
    cost_plane = load_and_process_file('costplane.csv')
    cost_train = load_and_process_file('costtrain.csv')
    cost_bus = load_and_process_file('costbus.csv')
    time_plane = load_and_process_file('timeplane.csv')
    time_train = load_and_process_file('timetrain.csv')
    time_bus = load_and_process_file('timebus.csv')

    # Load coordinates
    coordinates = pd.read_csv('xy.csv', delimiter=';')
    coordinates.set_index('City', inplace=True)
    
    seed = random.randint(0, 10000)
    random.seed(seed)
    
    combined_time_matrix, transport_time_matrix = combine_matrices_time(time_bus, time_train, time_plane, num_cities)
    combined_cost_matrix, transport_cost_matrix = combine_matrices_cost(cost_bus, cost_train, cost_plane, num_cities)
    
    toolbox.register("indices", random.sample, range(num_cities), num_cities)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("heuristic", custom_heuristic, combined_time_matrix, coordinates)
    
    if use_heuristic:
        population = toolbox.population(n=40-1)
        heuristic_solution = creator.Individual(toolbox.heuristic())
        population.append(heuristic_solution)
    else:
        population = toolbox.population(n=40)
        
    # Register the evaluation function
    toolbox.register("evaluate", evalTSPMulti, combined_cost_matrix=combined_cost_matrix, combined_time_matrix=combined_time_matrix)
    
    # Run the algorithm
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean, axis=0)
    stats.register("std", np.std, axis=0)
    stats.register("min", np.min, axis=0)
    stats.register("max", np.max, axis=0)
    
    algorithms.eaMuPlusLambda(population, toolbox, mu=40, lambda_=80, cxpb=0.7, mutpb=0.3, ngen=250, stats=stats, halloffame=hof, verbose=False)
    
    return population, stats, hof, combined_cost_matrix, combined_time_matrix, transport_cost_matrix, transport_time_matrix, coordinates

if __name__ == "__main__":    
    
    # Interactive input for number of cities
    while True:
        try:
            num_cities = int(input("Enter the number of cities (10, 30, 50): "))
            if num_cities not in [10, 30, 50]:
                raise ValueError
            break
        except ValueError:
            print("Invalid number of cities. Please enter 10, 30, or 50.")
    
    # Interactive input for the use of heuristics
    while True:
        use_heuristic = input("Use heuristic? (yes, no): ").strip().lower()
        if use_heuristic in ['yes', 'no']:
            use_heuristic = (use_heuristic == 'yes')
            break
        else:
            print("Invalid option. Please enter 'yes' or 'no'.")
    
    pop, stats, hof, combined_cost_matrix, combined_time_matrix, transport_cost_matrix, \
        transport_time_matrix, coordinates = main(num_cities, use_heuristic)
    
    # Plotting the Pareto curve
    pareto_front = tools.sortNondominated(pop, len(pop), first_front_only=True)[0]
    pareto_front.sort(key=lambda ind: ind.fitness.values[0])  # Sort by cost
    costs = [ind.fitness.values[0] for ind in pareto_front]
    times = [ind.fitness.values[1] for ind in pareto_front]
    plt.plot(costs, times, marker='o')
    plt.xlabel('Cost')
    plt.ylabel('Time')
    plt.title('Pareto Curve')
    plt.show()   
    
    # Find the best cost and best time individuals
    best_cost_individual = pareto_front[0]
    best_time_individual = min(pareto_front, key=lambda ind: ind.fitness.values[1])

    # Print coordinates of the best cost individual
    best_cost = best_cost_individual.fitness.values[0]
    best_cost_time = best_cost_individual.fitness.values[1]
    print(f"Best Cost Point Coordinates: Cost = {best_cost}, Time = {best_cost_time}")

    # Print coordinates of the best time individual
    best_time = best_time_individual.fitness.values[1]
    best_time_cost = best_time_individual.fitness.values[0]
    print(f"Best Time Point Coordinates: Cost = {best_time_cost}, Time = {best_time}")

    # Print the best cost and best time values
    #print(f"Best Cost: {best_cost}")
    #print(f"Best Time: {best_time}")

    # Plot the best cost path
    plot_path(best_cost_individual, combined_cost_matrix, coordinates, transport_cost_matrix)

    # Plot the best time path
    plot_path(best_time_individual, combined_time_matrix, coordinates, transport_time_matrix)
    
    # Calculate the hypervolume
    reference_point = [max(costs) * 1.1, max(times) * 1.1]  # Adjust reference point to be slightly larger than the max values
    
    hv_values = [ind.fitness.values for ind in pareto_front]
    hv_value = hv.hypervolume(hv_values, reference_point)
    print(f"Hypervolume: {hv_value}")

    # Plot the hypervolume area using the existing Pareto front plot
    hv_values_sorted = np.array(sorted(hv_values, key=lambda x: x[0]))
    hv_values_sorted = np.vstack((hv_values_sorted, reference_point))

    # Fill the area dominated by the Pareto front
    plt.fill_between(hv_values_sorted[:, 0], hv_values_sorted[:, 1], reference_point[1], step='post', alpha=0.3, label='Dominated Area')

    # Add hypervolume value to the legend
    plt.scatter([], [], color='none', label=f'Hypervolume: {hv_value:.2f}')
    
    # Plot the Pareto front points again to ensure they are visible
    plt.scatter(costs, times, color='blue', label='Pareto Front Points')

    # Plot the reference point
    plt.scatter(reference_point[0], reference_point[1], color='red', label='Reference Point')

    # Update the legend and show the plot
    plt.legend()
    plt.xlabel('Cost')
    plt.ylabel('Time')
    plt.title('Pareto Front and Hypervolume Evolution Curve')
    plt.show()