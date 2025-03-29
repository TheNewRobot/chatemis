import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
import numpy as np
from datetime import datetime

def load_and_preprocess_data(csv_file):
    """
    Load and preprocess the CSV data for plotting
    
    Args:
        csv_file (str): Path to the CSV file with parsed metrics
        
    Returns:
        pd.DataFrame: Preprocessed dataframe
    """
    # Load data
    df = pd.read_csv(csv_file)
    
    # Convert timestamp to datetime for proper plotting
    df['datetime'] = pd.to_datetime(df['timestamp'], format='%m-%d-%Y %H:%M:%S')
    
    # Calculate seconds from start
    start_time = df['datetime'].min()
    df['seconds'] = (df['datetime'] - start_time).dt.total_seconds()
    
    return df, start_time

def plot_memory_usage(ax, df, colors, x_min, x_max):
    """Plot Memory Usage"""
    ram_used = df['RAM_used'].astype(float)
    ram_total = df['RAM_total'].astype(float)
    ram_percent = (ram_used / ram_total) * 100
    
    ax.plot(df['seconds'], ram_percent, color=colors[0], linewidth=2, label='RAM Usage %')
    ax.set_ylabel('Memory Usage (%)')
    ax.set_title('Memory Utilization', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.set_xlim(x_min, x_max)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    return ax

def plot_cpu_usage(ax, df, colors, x_min, x_max):
    """Plot CPU Usage"""
    # Calculate average CPU usage across all cores
    cpu_cols = [col for col in df.columns if col.startswith('CPU') and col.endswith('_load')]
    df_cpu = df[cpu_cols].astype(float)
    avg_cpu = df_cpu.mean(axis=1)
    
    # Plot average CPU usage
    ax.plot(df['seconds'], avg_cpu, color=colors[1], linewidth=2, label='Avg CPU Usage')
    
    # Plot individual CPU cores with lighter lines
    for i, col in enumerate(cpu_cols):
        ax.plot(df['seconds'], df[col].astype(float), color=colors[i % len(colors)], 
                 alpha=0.3, linewidth=1, label=f'Core {i+1}')
    
    ax.set_ylabel('CPU Usage (%)')
    ax.set_title('CPU Utilization', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    return ax

def plot_temperature(ax, df, colors, x_min, x_max):
    """Plot Temperature"""
    temp_cols = [col for col in df.columns if col.endswith('_temp')]
    
    # Use a different color for each temperature sensor
    for i, col in enumerate(['cpu_temp', 'gpu_temp']):
        if col in df.columns:
            ax.plot(df['seconds'], df[col].astype(float), 
                     color=colors[i+2], linewidth=2, 
                     label=col.replace('_temp', '').upper())
    
    ax.set_ylabel('Temperature (°C)')
    ax.set_title('Component Temperatures', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    return ax

def plot_gpu_usage(ax, df, colors, x_min, x_max):
    """Plot GPU Usage"""
    ax.plot(df['seconds'], df['GR3D_FREQ'].astype(float), color=colors[4], linewidth=2)
    ax.set_ylabel('GPU Usage (%)')
    ax.set_title('GPU Utilization', fontsize=14, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3)
    
    return ax

def plot_power_consumption(ax, df, colors, x_min, x_max):
    """Plot Power Consumption"""
    # Only include certain power metrics for clarity
    power_cols = ['VDD_IN_current', 'VDD_CPU_GPU_CV_current', 'VDD_SOC_current']
    power_labels = ['System Total', 'CPU+GPU', 'SoC']
    
    for i, (col, label) in enumerate(zip(power_cols, power_labels)):
        ax.plot(df['seconds'], df[col].astype(float), 
                 color=colors[i+5], linewidth=2, label=label)
    
    ax.set_ylabel('Power (mW)')
    ax.set_xlabel('Time (seconds)')
    ax.set_title('Power Consumption', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right')
    
    return ax

def plot_jetson_metrics(csv_file, plots_to_include=None, save_figure=False, output_file="jetson_performance.png"):
    """
    Create a comprehensive visualization of Jetson performance metrics
    
    Args:
        csv_file (str): Path to the CSV file with parsed metrics
        plots_to_include (list): List of plot types to include. Options:
                                 ['memory', 'cpu', 'temperature', 'gpu', 'power']
                                 If None, all plots will be included.
        save_figure (bool): Whether to save the figure to a file
        output_file (str): Path to save the figure (if save_figure is True)
    """
    # Define default plot types if none specified
    if plots_to_include is None:
        plots_to_include = ['memory', 'cpu', 'temperature', 'gpu', 'power']
    
    # Validate plot types
    valid_plot_types = ['memory', 'cpu', 'temperature', 'gpu', 'power']
    for plot_type in plots_to_include:
        if plot_type not in valid_plot_types:
            raise ValueError(f"Invalid plot type: {plot_type}. Valid options are: {valid_plot_types}")
    
    # Load and preprocess data
    df, start_time = load_and_preprocess_data(csv_file)
    
    # Get start and end times (hours only)
    start_time_str = start_time.strftime('%H:%M:%S')
    end_time_str = df['datetime'].max().strftime('%H:%M:%S')
    
    # Calculate the min and max for x-axis limits
    x_min = df['seconds'].min()
    x_max = df['seconds'].max()
    
    # Map plot types to their corresponding functions
    plot_functions = {
        'memory': plot_memory_usage,
        'cpu': plot_cpu_usage,
        'temperature': plot_temperature,
        'gpu': plot_gpu_usage,
        'power': plot_power_consumption
    }
    
    # Filter to only include requested plot types
    plot_functions = {k: v for k, v in plot_functions.items() if k in plots_to_include}
    
    # Set up the figure with a grid for selected plots
    plt.style.use('ggplot')
    num_plots = len(plot_functions)
    
    # Adjust height ratios - power plot gets a bit more space
    height_ratios = [1] * num_plots
    if 'power' in plot_functions:
        power_index = list(plot_functions.keys()).index('power')
        height_ratios[power_index] = 1.5
    
    fig = plt.figure(figsize=(12, 3 * num_plots))
    gs = GridSpec(num_plots, 1, height_ratios=height_ratios)
    
    # Define a consistent color palette
    colors = plt.cm.tab10.colors
    
    # Initialize a shared x-axis for all plots
    shared_ax = None
    
    # Create each plot in order
    for i, (plot_type, plot_func) in enumerate(plot_functions.items()):
        # First plot or create a new plot sharing x-axis with the first
        if i == 0:
            ax = fig.add_subplot(gs[i])
            shared_ax = ax
        else:
            ax = fig.add_subplot(gs[i], sharex=shared_ax)
        
        # Call the appropriate plotting function
        plot_func(ax, df, colors, x_min, x_max)
    
    # Add text with start and end times
    time_info = f"Time range: {start_time_str} - {end_time_str}"
    fig.text(0.5, 0.01, time_info, ha='center', fontsize=10)
    
    # Add overall title
    plt.suptitle('Jetson Performance Profile', fontsize=16, fontweight='bold', y=0.98)
    
    # Adjust layout
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    # Save figure if requested
    if save_figure:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Figure saved to {output_file}")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    # Define input CSV file

    csv_file = "jetson_stats.csv"
    save_plot_path = 'plots/jetson_custom_view.png'
    fields = ['memory','cpu','power','temperature','gpu']

    plot_jetson_metrics(csv_file, plots_to_include=fields, 
                        save_figure=True, output_file=save_plot_path)