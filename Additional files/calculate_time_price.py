import pandas as pd

# Function to calculate bus cost
def calculate_bus_cost(input_file, output_file, multiplier=0.1):
    # Load the CSV file
    data = pd.read_csv(input_file, index_col=0)
    
    # Multiply the values by the specified multiplier and round
    costbus = (data * multiplier).round().astype(int)
    
    # Replace zeros with "-"
    costbus = costbus.replace(0, "-")
    
    # Replace values for Ireland and Iceland with "-"
    # Without bus: ['Dublin', 'Reykjavik', 'Oslo', 'Helsinki', 'Lisbon', 'Podgorica', 'Tirana']
    for city in ['Dublin', 'Reykjavik', 'Oslo', 'Helsinki', 'Lisbon','Podgorica', 'Tirana']:
        if city in costbus.columns:
            costbus[city] = "-"
        if city in costbus.index:
            costbus.loc[city] = "-"
    
    # Save the result in a new CSV file
    costbus.to_csv(output_file)
    print(f"The file '{output_file}' has been successfully created.")

# Function to calculate train cost
def calculate_train_cost(input_file, output_file_2, multiplier=0.2):
    # Load the CSV file
    data = pd.read_csv(input_file, index_col=0)
    
    # Multiply the values by the specified multiplier and round
    costtrain = (data * multiplier).round().astype(int)
    
    # Replace zeros with "-"
    costtrain = costtrain.replace(0, "-")
    
    # Replace values for Ireland and Iceland with "-"
    # without train: ['Dublin', 'Reykjavik', 'Athens', 'Sofia', 'Tallinn', 'Luxembourg', 'Vilnius']
    for city in ['Dublin', 'Reykjavik', 'Athens', 'Sofia', 'Tallinn', 'Luxembourg', 'Vilnius']:
        if city in costtrain.columns:
            costtrain[city] = "-"
        if city in costtrain.index:
            costtrain.loc[city] = "-"
    
    # Save the result in a new CSV file
    costtrain.to_csv(output_file_2)
    print(f"The file '{output_file_2}' has been successfully created.")

# Function to calculate airplane cost
def calculate_plane_cost(input_file, output_file_3, multiplier=0.1645):
    # Load the CSV file
    data = pd.read_csv(input_file, index_col=0)
    
    # Multiply the values by the specified multiplier and round
    costplane = (data * multiplier).round().astype(int)
    
    # Replace zeros with "-"
    costplane = costplane.replace(0, "-")
    
    # Without plane: ['Ljubljana', 'Bratislava', 'Chisinau', 'Sarajevo', 'Sofia', 'Bucharest', 'Zagreb']
    for city in ['Ljubljana', 'Bratislava', 'Chisinau', 'Sarajevo', 'Sofia', 'Bucharest', 'Zagreb']:
        if city in costplane.columns:
            costplane[city] = "-"
        if city in costplane.index:
            costplane.loc[city] = "-"
    
    # Save the result in a new CSV file
    costplane.to_csv(output_file_3)
    print(f"The file '{output_file_3}' has been successfully created.")

# Function to calculate bus travel time
def calculate_bus_time(input_file, output_file, speed=80):
    # Load the CSV file
    data = pd.read_csv(input_file, index_col=0)
    
    # Calculate travel time by dividing distance by speed and round to the nearest hour
    timebus = (data / speed).round().astype(int)
    
    # Replace zeros with "-"
    timebus = timebus.replace(0, "-")
    
    # Replace values for Ireland and Iceland with "-"
    # Without bus: ['Dublin', 'Reykjavik', 'Oslo', 'Helsinki', 'Lisbon', 'Podgorica', 'Tirana']
    for city in ['Dublin', 'Reykjavik', 'Oslo', 'Helsinki', 'Lisbon','Podgorica', 'Tirana']:
        if city in timebus.columns:
            timebus[city] = "-"
        if city in timebus.index:
            timebus.loc[city] = "-"
    
    # Save the result in a new CSV file
    timebus.to_csv(output_file)
    print(f"The file '{output_file}' has been successfully created.")

# Function to calculate train travel time
def calculate_train_time(input_file, output_file_2, speed=120):
    # Load the CSV file
    data = pd.read_csv(input_file, index_col=0)
    
    # Calculate travel time by dividing distance by speed and round to the nearest hour
    timetrain = (data / speed).round().astype(int)
    
    # Replace zeros with "-"
    timetrain = timetrain.replace(0, "-")
    
    # Replace values for Ireland and Iceland with "-"
    # without train: ['Dublin', 'Reykjavik', 'Athens', 'Sofia', 'Tallinn', 'Luxembourg', 'Vilnius']
    for city in ['Dublin', 'Reykjavik', 'Athens', 'Sofia', 'Tallinn', 'Luxembourg', 'Vilnius']:
        if city in timetrain.columns:
            timetrain[city] = "-"
        if city in timetrain.index:
            timetrain.loc[city] = "-"
    
    # Save the result in a new CSV file
    timetrain.to_csv(output_file_2)
    print(f"The file '{output_file_2}' has been successfully created.")

# Function to calculate airplane travel time
def calculate_plane_time(input_file, output_file_3, speed=567):
    # Load the CSV file
    data = pd.read_csv(input_file, index_col=0)
    
    # Calculate travel time by dividing distance by speed and round to the nearest hour
    timeplane = (data / speed).round().astype(int)
    
    # Replace zeros with "-"
    timeplane = timeplane.replace(0, "-")
    
    # Without plane: ['Ljubljana', 'Bratislava', 'Chisinau', 'Sarajevo', 'Sofia', 'Bucharest', 'Zagreb']
    for city in ['Ljubljana', 'Bratislava', 'Chisinau', 'Sarajevo', 'Sofia', 'Bucharest', 'Zagreb']:
        if city in timeplane.columns:
            timeplane[city] = "-"
        if city in timeplane.index:
            timeplane.loc[city] = "-"
    
    # Save the result in a new CSV file
    timeplane.to_csv(output_file_3)
    print(f"The file '{output_file_3}' has been successfully created.")

# Input and output parameters
input_file = 'matrix_distances.csv'
output_file = 'costbus.csv'
output_file_2 = 'costtrain.csv'
output_file_3 = 'costplane.csv'
output_time_bus = 'timebus.csv'
output_time_train = 'timetrain.csv'
output_time_plane = 'timeplane.csv'

# Execute the function
calculate_bus_cost(input_file, output_file)
calculate_train_cost(input_file, output_file_2)
calculate_plane_cost(input_file, output_file_3)
calculate_bus_time(input_file, output_time_bus)
calculate_train_time(input_file, output_time_train)
calculate_plane_time(input_file, output_time_plane)