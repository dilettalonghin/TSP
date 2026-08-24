import pandas as pd
import numpy as np

# Load data from CSV file
file_path = 'xy.csv'
data = pd.read_csv(file_path, delimiter=';')

# Function to calculate the distance between two points using the Haversine formula
def haversine(lat1, lon1, lat2, lon2, R=6371):
    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Difference in latitude and longitude
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine formula
    a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Return the rounded value as an integer
    return int(round(R * c))

# Get the list of cities
cities = data['City']
n_cities = len(cities)

# Create an empty distance matrix with dtype int for integers
distance_matrix = np.zeros((n_cities, n_cities), dtype=int)

# Calculate the Haversine distance between all pairs of cities
for i in range(n_cities):
    for j in range(n_cities):
        if i != j:  # Avoid calculating the distance of the city to itself
            city1 = data.iloc[i]
            city2 = data.iloc[j]
            distance_matrix[i, j] = haversine(city1['Latitude'], city1['Longitude'], 
                                              city2['Latitude'], city2['Longitude'])

# Create a DataFrame from the distance matrix
distance_df = pd.DataFrame(distance_matrix, index=cities, columns=cities)

# Save the DataFrame to a CSV file
output_path = 'matrix_distances.csv'
distance_df.to_csv(output_path)

print(f"The distance matrix has been saved to {output_path}")