import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from adjustText import adjust_text

# Load city data
file_path = 'xy.csv'
data = pd.read_csv(file_path, delimiter=';')

# Create a geometry column from the coordinates
geometry = [Point(xy) for xy in zip(data['Longitude'], data['Latitude'])]
geo_df = gpd.GeoDataFrame(data, geometry=geometry)

# Set the coordinate reference system
geo_df = geo_df.set_crs(epsg=4326)
geo_df = geo_df.to_crs(epsg=3857)

# Create the plot
fig, ax = plt.subplots(figsize=(15, 10))

# Plot the cities
geo_df.plot(ax=ax, markersize=20, color='red', marker='o', label='Cities')  # Reduced marker size

# Add labels for each city
texts = []
for x, y, label in zip(geo_df.geometry.x, geo_df.geometry.y, geo_df['City']):
    texts.append(ax.text(x, y, label, fontsize=5, ha='right'))  # Reduced font size

# Adjust the plot limits to cover all cities with an extra margin
margin = 0.1  # 10% margin
x_min, y_min, x_max, y_max = geo_df.total_bounds
ax.set_xlim(x_min - (x_max - x_min) * margin, x_max + (x_max - x_min) * margin)
ax.set_ylim(y_min - (y_max - y_min) * margin, y_max + (y_max - y_min) * margin)

# Add basemap with contextily and set the zoom level
ctx.add_basemap(ax, crs=geo_df.crs.to_string(), source=ctx.providers.CartoDB.PositronNoLabels, zoom=4)

# Adjust text to avoid overlap
adjust_text(texts, 
            only_move={'points': 'xy', 'texts': 'xy'},  # Allow movement in both x and y directions
            arrowprops=dict(arrowstyle='-', color='gray', lw=0.5),
            expand_text=(1.2, 1.4),  # Expand the space around the text
            expand_points=(1.2, 1.4),  # Expand the space around the points
            force_text=1.0,  # Increase the force to separate text
            force_points=1.0)  # Increase the force to separate points

# Set the title and axis labels
plt.title('Planar Map of Selected Cities in Europe')
plt.xlabel('Longitude')
plt.ylabel('Latitude')

# Show the plot
plt.grid(True)
plt.show()