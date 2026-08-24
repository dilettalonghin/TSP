import json
import matplotlib.pyplot as plt

def load_convergence_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def plot_convergence_curves(file_paths, labels, title, ylabel):
    plt.figure(figsize=(10, 6))
    for file_path, label in zip(file_paths, labels):
        convergence_data = load_convergence_data(file_path)
        generations = range(len(convergence_data))
        plt.plot(generations, convergence_data, label=label)
    
    plt.xlabel('# Generations')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":

    # Plot 1
    file_paths_plot1 = [
        'cost_bus.json',
        'cost_train.json',
        'cost_plane.json',
        'cost_all.json'
    ]
    labels_plot1 = ['Bus', 'Train', 'Plane', 'All']
    plot_convergence_curves(file_paths_plot1, labels_plot1, 'Convergence Curves (mCost)', 'Total Cost')

    # Plot 2
    file_paths_plot2 = [
        'time_bus.json',
        'time_train.json',
        'time_plane.json',
        'time_all.json'
    ]
    labels_plot2 = ['Bus', 'Train', 'Plane', 'All']
    plot_convergence_curves(file_paths_plot2, labels_plot2, 'Convergence Curves (mTime)', 'Total Time')