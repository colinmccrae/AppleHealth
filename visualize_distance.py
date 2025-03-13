#!/usr/bin/env python3
"""
Visualizes walking and running distance data from Apple Health.
Creates charts showing trends over time and patterns in distance traveled.
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

def load_distance_data(data_dir='data', filename='distance_data.json'):
    """Load distance data from JSON file in the specified directory."""
    json_path = os.path.join(data_dir, filename)
    
    # Check if file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Data file not found at '{json_path}'. Please run extract_distance.py first.")
    
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

def plot_distance_chart(data, year=None, output_dir='outputs'):
    """Create visualization for walking/running distance."""
    # Extract dates and values
    dates = [entry['date'] for entry in data]
    distance_values = [entry['distance_km'] for entry in data]
    
    # Set default output file based on year
    year_str = f"_{year}" if year else ""
    output_file = os.path.join(output_dir, f"distance_chart{year_str}.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Calculate moving average (7-day window)
    window_size = 7
    moving_avg = calculate_moving_average(distance_values, window_size)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Define colors
    bar_color = '#4CAF50'  # green
    line_color = '#3a7ebf'  # blue
    
    # Create bar chart
    plt.bar(dates_mdates, distance_values, label='Daily Distance', color=bar_color, alpha=0.7)
    
    # Plot 7-day moving average
    plt.plot(dates_mdates, moving_avg, color=line_color, linewidth=2.5, 
             label=f'{window_size}-Day Moving Average')
    
    # Add reference lines for common distance goals
    plt.axhline(y=5, color='#ffa726', linestyle='--', alpha=0.5, label='5 km Goal')
    plt.axhline(y=10, color='#e55934', linestyle='--', alpha=0.5, label='10 km Goal')
    
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
    plt.ylabel('Distance (km)')
    
    # Add grid, legend and title
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Set title based on year
    title = f"Walking/Running Distance in {year}" if year else "Walking/Running Distance Over All Years"
    plt.title(title)
    
    # Calculate statistics
    avg_distance = sum(distance_values) / len(distance_values)
    min_distance = min(distance_values)
    max_distance = max(distance_values)
    total_distance = sum(distance_values)
    days_over_5km = sum(1 for d in distance_values if d >= 5)
    days_over_10km = sum(1 for d in distance_values if d >= 10)
    
    # Add text box with statistics
    stats_text = (
        f"Days recorded: {len(dates)}\n"
        f"Total distance: {total_distance:.1f} km\n"
        f"Average: {avg_distance:.2f} km/day\n"
        f"Days ≥ 5 km: {days_over_5km} ({days_over_5km/len(dates)*100:.1f}%)\n"
        f"Days ≥ 10 km: {days_over_10km} ({days_over_10km/len(dates)*100:.1f}%)"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Distance chart saved as '{output_file}'")
    plt.close()

def plot_cumulative_distance(data, output_dir='outputs'):
    """Create a visualization of cumulative distance over time."""
    # Extract dates and sort by date
    sorted_data = sorted(data, key=lambda x: x['date'])
    dates = [entry['date'] for entry in sorted_data]
    distances = [entry['distance_km'] for entry in sorted_data]
    
    # Calculate cumulative distance
    cumulative_distance = np.cumsum(distances)
    
    # Set output file
    output_file = os.path.join(output_dir, "cumulative_distance_chart.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot cumulative distance
    plt.plot(dates_mdates, cumulative_distance, color='#3a7ebf', linewidth=2.5)
    
    # Configure x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gcf().autofmt_xdate()
    
    # Configure y-axis
    plt.ylabel('Cumulative Distance (km)')
    
    # Format y-axis labels with commas for thousands
    plt.gca().get_yaxis().set_major_formatter(
        plt.matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    
    # Add grid and title
    plt.grid(True, alpha=0.3)
    plt.title('Cumulative Walking/Running Distance Over Time')
    
    # Calculate statistics
    total_distance = cumulative_distance[-1]
    total_days = len(dates)
    avg_daily = total_distance / total_days if total_days > 0 else 0
    
    # Calculate interesting milestones
    marathon = 42.195
    marathons = total_distance / marathon
    earth_circumference = 40075
    earth_percent = (total_distance / earth_circumference) * 100
    
    # Add text box with statistics
    stats_text = (
        f"Total distance: {total_distance:.1f} km\n"
        f"Days recorded: {total_days}\n"
        f"Average per day: {avg_daily:.2f} km\n"
        f"Equivalent to: {marathons:.1f} marathons\n"
        f"Earth circumference: {earth_percent:.2f}%"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Cumulative distance chart saved as '{output_file}'")
    plt.close()

def plot_monthly_averages(data, output_dir='outputs'):
    """Create a chart showing average distance by month across all years."""
    from collections import defaultdict
    
    # Group by year and month
    monthly_data = defaultdict(list)
    
    for entry in data:
        date = entry['date']
        # Create a key in the format (year, month)
        key = (date.year, date.month)
        monthly_data[key].append(entry['distance_km'])
    
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
    output_file = os.path.join(output_dir, "monthly_distance_averages.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot monthly averages with colorization
    bars = plt.bar(range(len(avg_values)), avg_values)
    
    # Color bars based on average distance
    for i, bar in enumerate(bars):
        if avg_values[i] < 2:
            bar.set_color('#e55934')  # red
        elif avg_values[i] < 5:
            bar.set_color('#ffa726')  # orange
        else:
            bar.set_color('#4CAF50')  # green
    
    # Add reference lines for common goals
    plt.axhline(y=2, color='#e55934', linestyle='--', alpha=0.3, label='2 km')
    plt.axhline(y=5, color='#ffa726', linestyle='--', alpha=0.3, label='5 km')
    
    # Configure x-axis
    plt.xticks(range(len(avg_values)), month_labels, rotation=90)
    
    # Configure y-axis
    plt.ylabel('Average Daily Distance (km)')
    
    # Add grid, legend and title
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend()
    plt.title('Average Daily Walking/Running Distance by Month')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Monthly distance averages chart saved as '{output_file}'")
    plt.close()

def plot_distance_histogram(data, output_dir='outputs'):
    """Create a histogram showing the distribution of daily distance values."""
    # Extract distance values
    distance_values = [entry['distance_km'] for entry in data]
    
    # Set output file
    output_file = os.path.join(output_dir, "distance_histogram.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Create histogram with a reasonable number of bins
    max_dist = max(distance_values)
    bin_width = 0.5  # 0.5 km per bin
    num_bins = int(max_dist / bin_width) + 1
    
    n, bins, patches = plt.hist(distance_values, bins=num_bins, alpha=0.7, color='#3a7ebf')
    
    # Color the bins based on distance
    for i, p in enumerate(patches):
        if bins[i] < 2:
            p.set_facecolor('#e55934')  # red
        elif bins[i] < 5:
            p.set_facecolor('#ffa726')  # orange
        else:
            p.set_facecolor('#4CAF50')  # green
    
    # Add vertical lines for key distances
    plt.axvline(x=2, color='#e55934', linestyle='--', alpha=0.5, label='2 km')
    plt.axvline(x=5, color='#ffa726', linestyle='--', alpha=0.5, label='5 km')
    plt.axvline(x=10, color='#4CAF50', linestyle='--', alpha=0.5, label='10 km')
    
    # Configure axes
    plt.xlabel('Daily Distance (km)')
    plt.ylabel('Frequency (Days)')
    plt.grid(True, alpha=0.3, axis='y')
    plt.title('Distribution of Daily Walking/Running Distances')
    plt.legend()
    
    # Calculate statistics
    avg_distance = sum(distance_values) / len(distance_values)
    median_distance = sorted(distance_values)[len(distance_values)//2]
    
    # Add statistics annotation
    stats_text = (
        f"Total days: {len(distance_values)}\n"
        f"Mean distance: {avg_distance:.2f} km\n"
        f"Median distance: {median_distance:.2f} km\n"
        f"Range: {min(distance_values):.2f} - {max(distance_values):.2f} km"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Distance histogram saved as '{output_file}'")
    plt.close()

if __name__ == "__main__":
    # Set directories
    DATA_DIR = 'data'
    OUTPUT_DIR = 'outputs'
    
    # Load data
    try:
        print("Starting chart generation process...")
        distance_data = load_distance_data(data_dir=DATA_DIR)
        
        # Ensure output directory exists
        ensure_dir(OUTPUT_DIR)
        print(f"All charts will be saved to the '{OUTPUT_DIR}' directory")
        
        # Create chart for all data
        print("\nGenerating chart for all years combined...")
        plot_distance_chart(distance_data, output_dir=OUTPUT_DIR)
        
        # Create cumulative distance chart
        print("\nGenerating cumulative distance chart...")
        plot_cumulative_distance(distance_data, output_dir=OUTPUT_DIR)
        
        # Create monthly averages chart
        print("\nGenerating monthly averages chart...")
        plot_monthly_averages(distance_data, output_dir=OUTPUT_DIR)
        
        # Create histogram
        print("\nGenerating distance histogram...")
        plot_distance_histogram(distance_data, output_dir=OUTPUT_DIR)
        
        # Group data by year
        print("\nGrouping data by year...")
        years_data = group_by_year(distance_data)
        years = sorted(years_data.keys())
        print(f"Found data for years: {', '.join(map(str, years))}")
        
        # Create charts for each year
        for year in years:
            print(f"\nGenerating chart for year {year}...")
            year_data = years_data[year]
            
            # Only create charts if there's enough data (more than 30 days)
            if len(year_data) >= 30:
                plot_distance_chart(year_data, year, output_dir=OUTPUT_DIR)
            else:
                print(f"Skipping year {year} - not enough data (only {len(year_data)} days)")
        
        print(f"\nAll charts saved to '{OUTPUT_DIR}/' directory")
        print("Charts generated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")