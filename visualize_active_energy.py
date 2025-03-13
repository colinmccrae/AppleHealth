#!/usr/bin/env python3
"""
Visualizes daily active energy burned data from Apple Health.
Creates charts showing daily active calories and trends over time.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import json
import os

def ensure_dir(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    return directory

def load_active_energy_data(data_dir='data', filename='active_energy_data.json'):
    """Load active energy data from JSON file in the specified directory."""
    json_path = os.path.join(data_dir, filename)
    
    # Check if file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Data file not found at '{json_path}'. Please run extract_active_energy.py first.")
    
    print(f"Loading data from {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Convert date strings back to datetime.date objects
    for entry in data:
        entry['date'] = datetime.fromisoformat(entry['date']).date()
    
    return data

def calculate_moving_average(data, window_size):
    """Calculate moving average for a data series."""
    moving_avg = []
    
    for i in range(len(data)):
        if i < window_size - 1:
            window = data[:i+1]
        else:
            window = data[i-window_size+1:i+1]
        moving_avg.append(sum(window) / len(window))
    
    return moving_avg

def group_by_year(data):
    """Group data by year."""
    years_data = {}
    
    for entry in data:
        year = entry['date'].year
        if year not in years_data:
            years_data[year] = []
        years_data[year].append(entry)
    
    return years_data

def plot_active_energy_chart(data, year=None, output_dir='outputs'):
    """Create visualization for active energy burned."""
    # Extract dates and values
    dates = [entry['date'] for entry in data]
    active_calories = [entry['active_calories'] for entry in data]
    
    # Set default output file based on year
    year_str = f"_{year}" if year else ""
    output_file = os.path.join(output_dir, f"active_energy_chart{year_str}.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Calculate moving average (7-day window)
    window_size = 7
    moving_avg = calculate_moving_average(active_calories, window_size)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Define colors
    bar_color = '#e55934'  # orange-red
    line_color = '#3a7ebf'  # blue
    
    # Create bar chart
    plt.bar(dates_mdates, active_calories, label='Active Calories', color=bar_color, alpha=0.7)
    
    # Plot 7-day moving average
    plt.plot(dates_mdates, moving_avg, color=line_color, linewidth=2.5, 
             label=f'{window_size}-Day Moving Average')
    
    # Configure x-axis
    if year:
        # For single year charts, show months
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
    else:
        # For all data, show year-month
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    
    plt.gcf().autofmt_xdate()
    
    # Configure y-axis
    max_calories = max(active_calories) * 1.1  # Add 10% headroom
    plt.ylim(0, max_calories)
    plt.ylabel('Active Calories (kcal)')
    
    # Add grid, legend and title
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Set title based on year
    title = f"Active Energy Burned in {year}" if year else "Active Energy Burned Over All Years"
    plt.title(title)
    
    # Calculate statistics
    avg_calories = sum(active_calories) / len(active_calories)
    min_calories = min(active_calories)
    max_calories = max(active_calories)
    
    # Add text box with statistics
    stats_text = (
        f"Days recorded: {len(dates)}\n"
        f"Average: {avg_calories:.2f} kcal\n"
        f"Min: {min_calories:.2f} kcal\n"
        f"Max: {max_calories:.2f} kcal"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Active energy chart saved as '{output_file}'")
    plt.close()

def plot_monthly_averages(data, output_dir='outputs'):
    """Create a chart showing average active energy by month across all years."""
    from collections import defaultdict
    
    # Group by year and month
    monthly_data = defaultdict(list)
    
    for entry in data:
        date = entry['date']
        # Create a key in the format (year, month)
        key = (date.year, date.month)
        monthly_data[key].append(entry['active_calories'])
    
    # Calculate monthly averages
    monthly_avgs = {}
    for (year, month), values in monthly_data.items():
        monthly_avgs[(year, month)] = sum(values) / len(values)
    
    # Sort by date
    sorted_months = sorted(monthly_avgs.keys())
    
    # Create x-axis labels and y-axis values
    month_labels = [f"{year}-{month:02d}" for year, month in sorted_months]
    avg_values = [monthly_avgs[key] for key in sorted_months]
    
    # Set output file
    output_file = os.path.join(output_dir, "monthly_active_energy_averages.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot monthly averages
    plt.bar(range(len(avg_values)), avg_values, color='#4CAF50')
    
    # Configure x-axis
    plt.xticks(range(len(avg_values)), month_labels, rotation=90)
    
    # Configure y-axis
    plt.ylabel('Average Active Calories (kcal)')
    
    # Add grid and title
    plt.grid(True, alpha=0.3, axis='y')
    plt.title('Average Daily Active Energy by Month')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Monthly averages chart saved as '{output_file}'")
    plt.close()

if __name__ == "__main__":
    # Set directories
    DATA_DIR = 'data'
    OUTPUT_DIR = 'outputs'
    
    # Load data
    try:
        print("Starting chart generation process...")
        active_energy_data = load_active_energy_data(data_dir=DATA_DIR)
        
        # Ensure output directory exists
        ensure_dir(OUTPUT_DIR)
        print(f"All charts will be saved to the '{OUTPUT_DIR}' directory")
        
        # Create chart for all data
        print("\nGenerating chart for all years combined...")
        plot_active_energy_chart(active_energy_data, output_dir=OUTPUT_DIR)
        
        # Create monthly averages chart
        print("\nGenerating monthly averages chart...")
        plot_monthly_averages(active_energy_data, output_dir=OUTPUT_DIR)
        
        # Group data by year
        print("\nGrouping data by year...")
        years_data = group_by_year(active_energy_data)
        years = sorted(years_data.keys())
        print(f"Found data for years: {', '.join(map(str, years))}")
        
        # Create charts for each year
        for year in years:
            print(f"\nGenerating chart for year {year}...")
            year_data = years_data[year]
            
            # Only create charts if there's enough data (more than 30 days)
            if len(year_data) >= 30:
                plot_active_energy_chart(year_data, year, output_dir=OUTPUT_DIR)
            else:
                print(f"Skipping year {year} - not enough data (only {len(year_data)} days)")
        
        print(f"\nAll charts saved to '{OUTPUT_DIR}/' directory")
        print("Charts generated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")