import pandas as pd
import numpy as np
from deap import base, creator, tools, algorithms
import random
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from adjustText import adjust_text
import json

def load_and_process_file(file_path):
    cost_time_df = pd.read_csv(file_path, delimiter=',', na_values="-")
    cost_time_df = cost_time_df.fillna(float('inf'))
    cost_time_df = cost_time_df.set_index(cost_time_df.columns[0])
    return cost_time_df


def filter_reachable_cities(matrix):
    reachable = matrix.applymap(lambda x: x != float('inf')).any(axis=1)
    filtered_matrix = matrix.loc[reachable.index[reachable], reachable.index[reachable]]
    return filtered_matrix

def sort_and_filter_matrix(matrix, num_cities):
    # Sort the first num_cities in alphabetical order
    cities = sorted(matrix.index)[:num_cities]
    filtered_matrix = matrix.loc[cities, cities]
    return filtered_matrix

# Defining the fitness function
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# Creating the toolbox
toolbox = base.Toolbox()

# Genetic operators
toolbox.register("mate", tools.cxOrdered)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def evalTSP(individual, filtered_matrix):
    total_cost_time = 0
    penalty = 1e6  # Maintain a moderate penalty
    inf_connections = 0  # Number of infinite connections

    for i in range(len(individual) - 1):
        cost_time = filtered_matrix.iloc[individual[i], individual[i + 1]]
        if cost_time == float('inf'):
            inf_connections += 1
        total_cost_time += cost_time

    # Add cost for returning to the starting city
    cost_time = filtered_matrix.iloc[individual[-1], individual[0]]
    if cost_time == float('inf'):
        inf_connections += 1
    total_cost_time += cost_time

    # Apply penalty for infinite connections
    total_cost_time += inf_connections * penalty

    return total_cost_time,

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
    
def plot_convergence_curve(convergence_data):
    plt.figure(figsize=(10, 6))
    plt.plot(convergence_data, label='Best Cost/Time')
    plt.xlabel('Generation')
    plt.ylabel('Cost/Time')
    plt.title('Convergence Curve')
    plt.legend()
    plt.grid(True)
    plt.show()

def calculate_and_print_stats(results):
    mean_result = np.mean(results)
    std_result = np.std(results, ddof=1) # Use ddof=1 for sample standard deviation

    print(f'Mean of best time/cost: {mean_result}')
    print(f'Standard deviation of best time/cost: {std_result}')

def custom_heuristic(filtered_matrix, coordinates):
    # Filter coordinates to include only cities present in the filtered_matrix
    filtered_coordinates = coordinates.loc[filtered_matrix.index]
    
    # Divide cities into bottom half and top half
    median_y = filtered_coordinates['Latitude'].median()
    print(f"Median latitude: {median_y}")  # Print the median latitude
    
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
    tour_indices = [filtered_matrix.index.get_loc(city) for city in tour]
    print(f"Custom heuristic tour: {tour_indices}")
    
    return tour_indices

def main(filtered_matrix, coordinates, num_cities, transport_matrix, num_runs, use_heuristic, seed=None, pop_size=40, num_generations=250, cxpb=0.8, mutpb=0.3):
    
    if seed is not None:
        random.seed(seed)

    # Register the individual and population
    toolbox.register("indices", random.sample, range(num_cities), num_cities)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("heuristic_individual", custom_heuristic, filtered_matrix=filtered_matrix, coordinates=coordinates)
    
    if use_heuristic:
        pop = toolbox.population(n=pop_size - 1)
        heuristic_solution = creator.Individual(toolbox.heuristic_individual())
        pop.append(heuristic_solution)
    else:
        # Create initial population
        pop = toolbox.population(n=pop_size)

    # Register the evaluation function with the filtered cost matrix
    toolbox.register("evaluate", evalTSP, filtered_matrix=filtered_matrix)
    
    hall_of_fame = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min)

    pop, logbook = algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=num_generations, 
                                       stats=stats, halloffame=hall_of_fame, verbose=False)

    best_ind = hall_of_fame[0]
    best_cost_time = evalTSP(best_ind, filtered_matrix)[0]
    #print(f'Best individual: {best_ind}')
    #print(f'Best time / cost: {best_cost_time}')

    # Plot the best path only if the num_runs is 1
    if num_runs == 1:
        plot_path(best_ind, filtered_matrix, coordinates, transport_matrix)        
    
    return best_cost_time, logbook.select("min")    

if __name__ == "__main__":
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

    # Interactive input
    while True:
        try:
            num_cities = int(input("Enter the number of cities (10, 30, 50): "))
            if num_cities not in [10, 30, 50]:
                raise ValueError
            break
        except ValueError:
            print("Invalid number of cities. Please enter 10, 30, or 50.")

    while True:
        criterion = input("Evaluate by cost or time? (cost, time): ").strip().lower()
        if criterion in ['cost', 'time']:
            break
        else:
            print("Invalid criterion. Please enter 'cost' or 'time'.")

    while True:
        transport = input("Choose transport (bus, train, plane, all): ").strip().lower()
        if transport in ['bus', 'train', 'plane', 'all']:
            break
        else:
            print("Invalid transport option. Please enter 'bus', 'train', 'plane', or 'all'.")
    
    while True:
        num_runs = input("How many runs? [1; 30]: ").strip()
        if num_runs.isdigit() and 1 <= int(num_runs) <= 30:
            num_runs = int(num_runs)
            break
        else:
            print("Invalid number of runs. Please enter a number between 1 and 30.")
    
    while True:
        use_heuristic = input("Use heuristic? (yes, no): ").strip().lower()
        if use_heuristic in ['yes', 'no']:
            use_heuristic = (use_heuristic == 'yes')
            break
        else:
            print("Invalid option. Please enter 'yes' or 'no'.")
    
    
    results = []  # List to store the results of each run
    best_run_convergence = None
    best_run_result = float('inf')
    
    # Run the algorithm num_runs times
    for i in range(num_runs):  
        seed = random.randint(0, 10000)  # Generate a random seed          
        if criterion == 'cost':
            if transport == 'bus':                
                filtered_cost_bus = filter_reachable_cities(cost_bus)
                filtered_cost_bus = sort_and_filter_matrix(filtered_cost_bus, num_cities)
                result, convergence_data = main(filtered_cost_bus, coordinates, num_cities, transport_matrix=pd.DataFrame('bus', index=filtered_cost_bus.index, columns=filtered_cost_bus.columns), num_runs=num_runs, use_heuristic=use_heuristic)
            elif transport == 'train':
                filtered_cost_train = filter_reachable_cities(cost_train)
                filtered_cost_train = sort_and_filter_matrix(filtered_cost_train, num_cities)
                result, convergence_data = main(filtered_cost_train, coordinates, num_cities, transport_matrix=pd.DataFrame('train', index=filtered_cost_train.index, columns=filtered_cost_train.columns), num_runs=num_runs, use_heuristic=use_heuristic)
            elif transport == 'plane':
                filtered_cost_plane = filter_reachable_cities(cost_plane)
                filtered_cost_plane = sort_and_filter_matrix(filtered_cost_plane, num_cities)
                result, convergence_data = main(filtered_cost_plane, coordinates, num_cities, transport_matrix=pd.DataFrame('plane', index=filtered_cost_plane.index, columns=filtered_cost_plane.columns), num_runs=num_runs, use_heuristic=use_heuristic)
            elif transport == 'all':
                filtered_cost_bus = sort_and_filter_matrix(cost_bus, num_cities)
                filtered_cost_train = sort_and_filter_matrix(cost_train, num_cities)
                filtered_cost_plane = sort_and_filter_matrix(cost_plane, num_cities)
                # Create combined cost matrix based on the lowest cost
                combined_cost_matrix = pd.DataFrame(index=filtered_cost_plane.index, columns=filtered_cost_plane.columns)
                transport_matrix = pd.DataFrame(index=filtered_cost_plane.index, columns=filtered_cost_plane.columns)
                for i in filtered_cost_plane.index:
                    for j in filtered_cost_plane.columns:
                        costs = {'bus': filtered_cost_bus.loc[i, j], 'train': filtered_cost_train.loc[i, j], 'plane': filtered_cost_plane.loc[i, j]}
                        min_cost_transport = min(costs, key=costs.get)
                        min_cost = costs[min_cost_transport]
                        if min_cost == float('inf'):
                            combined_cost_matrix.loc[i, j] = float('inf')
                            transport_matrix.loc[i, j] = 'none'
                        else:
                            combined_cost_matrix.loc[i, j] = min_cost
                            transport_matrix.loc[i, j] = min_cost_transport
                
                result, convergence_data = main(combined_cost_matrix, coordinates, num_cities, transport_matrix, num_runs=num_runs, use_heuristic=use_heuristic)
        elif criterion == 'time':
            if transport == 'bus':
                filtered_time_bus = filter_reachable_cities(time_bus)
                filtered_time_bus = sort_and_filter_matrix(filtered_time_bus, num_cities)                
                result, convergence_data = main(filtered_time_bus, coordinates, num_cities, transport_matrix=pd.DataFrame('bus', index=filtered_time_bus.index, columns=filtered_time_bus.columns), num_runs=num_runs, use_heuristic=use_heuristic)
            elif transport == 'train':
                filtered_time_train = filter_reachable_cities(time_train)
                filtered_time_train = sort_and_filter_matrix(filtered_time_train, num_cities)
                result, convergence_data = main(filtered_time_train, coordinates, num_cities, transport_matrix=pd.DataFrame('train', index=filtered_time_train.index, columns=filtered_time_train.columns), num_runs=num_runs, use_heuristic=use_heuristic)
            elif transport == 'plane':
                filtered_time_plane = filter_reachable_cities(time_plane)
                filtered_time_plane = sort_and_filter_matrix(filtered_time_plane, num_cities)
                result, convergence_data = main(filtered_time_plane, coordinates, num_cities, transport_matrix=pd.DataFrame('plane', index=filtered_time_plane.index, columns=filtered_time_plane.columns), num_runs=num_runs, use_heuristic=use_heuristic)
            elif transport == 'all':
                filtered_time_bus = sort_and_filter_matrix(time_bus, num_cities)
                filtered_time_train = sort_and_filter_matrix(time_train, num_cities)
                filtered_time_plane = sort_and_filter_matrix(time_plane, num_cities)
                # Create combined time matrix based on the lowest time
                combined_time_matrix = pd.DataFrame(index=filtered_time_plane.index, columns=filtered_time_plane.columns)
                transport_matrix = pd.DataFrame(index=filtered_time_plane.index, columns=filtered_time_plane.columns)
                for i in filtered_time_plane.index:
                    for j in filtered_time_plane.columns:
                        times = {'bus': filtered_time_bus.loc[i, j], 'train': filtered_time_train.loc[i, j], 'plane': filtered_time_plane.loc[i, j]}
                        min_time_transport = min(times, key=times.get)
                        min_time = times[min_time_transport]
                        
                        if min_time == float('inf'):
                            combined_time_matrix.loc[i, j] = float('inf')
                            transport_matrix.loc[i, j] = 'none'
                        else:
                            combined_time_matrix.loc[i, j] = min_time
                            transport_matrix.loc[i, j] = min_time_transport
                
                result, convergence_data = main(combined_time_matrix, coordinates, num_cities, transport_matrix, num_runs=num_runs, use_heuristic=use_heuristic)
        
        results.append(result)  # Store the result of the current run
        if result < best_run_result:
            best_run_result = result
            best_run_convergence = convergence_data
            
    # Calculate and print mean and standard deviation
    calculate_and_print_stats(results)
       
    if best_run_convergence is not None:
        plot_convergence_curve(best_run_convergence)
            
    #     # Save the best convergence data to a file
    #     if best_run_convergence is not None:
    #         with open('h_time_50.json', 'w') as f:
    #             json.dump(best_run_convergence, f)