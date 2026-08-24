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
        'h_cost_10.json',
        'h_cost_30.json',
        'h_cost_50.json'
    ]
    labels_plot1 = ['10 cities', '30 Cities', '50 Cities']
    plot_convergence_curves(file_paths_plot1, labels_plot1, 'Convergence Curves (mCost)', 'Total Cost')

    # Plot 2
    file_paths_plot2 = [
        'h_time_10.json',
        'h_time_30.json',
        'h_time_50.json'
    ]
    labels_plot2 = ['10 cities', '30 Cities', '50 Cities']
    plot_convergence_curves(file_paths_plot2, labels_plot2, 'Convergence Curves (mTime)', 'Total Time')