#!/usr/bin/env python3
"""
Visualizes resting heart rate data from Apple Health.
Creates charts showing trends over time and patterns in resting heart rate.
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

def load_resting_hr_data(data_dir='data', filename='resting_hr_data.json'):
    """Load resting heart rate data from JSON file in the specified directory."""
    json_path = os.path.join(data_dir, filename)
    
    # Check if file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Data file not found at '{json_path}'. Please run extract_resting_hr.py first.")
    
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

def plot_resting_hr_chart(data, year=None, output_dir='outputs'):
    """Create visualization for resting heart rate."""
    # Extract dates and values
    dates = [entry['date'] for entry in data]
    rhr_values = [entry['resting_hr'] for entry in data]
    
    # Set default output file based on year
    year_str = f"_{year}" if year else ""
    output_file = os.path.join(output_dir, f"resting_hr_chart{year_str}.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Calculate moving average (7-day window)
    window_size = 7
    moving_avg = calculate_moving_average(rhr_values, window_size)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Define colors
    scatter_color = '#e55934'  # orange-red
    line_color = '#3a7ebf'  # blue
    
    # Create scatter plot for individual readings
    plt.scatter(dates_mdates, rhr_values, label='Daily RHR', color=scatter_color, alpha=0.7, s=30)
    
    # Plot 7-day moving average
    plt.plot(dates_mdates, moving_avg, color=line_color, linewidth=2.5, 
             label=f'{window_size}-Day Moving Average')
    
    # Add reference zones for heart rate interpretations
    plt.axhspan(40, 60, alpha=0.1, color='green', label='Athletic/Excellent (40-60 bpm)')
    plt.axhspan(60, 70, alpha=0.1, color='lightgreen', label='Good (60-70 bpm)')
    plt.axhspan(70, 80, alpha=0.1, color='yellow', label='Average (70-80 bpm)')
    plt.axhspan(80, 90, alpha=0.1, color='orange', label='Below Average (80-90 bpm)')
    plt.axhspan(90, 100, alpha=0.1, color='red', label='Poor (>90 bpm)')
    
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
    min_rhr = min(min(rhr_values) - 5, 40)  # Lower limit at least 40 or 5 below minimum
    max_rhr = max(max(rhr_values) + 5, 100)  # Upper limit at least 100 or 5 above maximum
    plt.ylim(min_rhr, max_rhr)
    plt.ylabel('Resting Heart Rate (bpm)')
    
    # Add grid, legend and title
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Set title based on year
    title = f"Resting Heart Rate in {year}" if year else "Resting Heart Rate Over All Years"
    plt.title(title)
    
    # Calculate statistics
    avg_rhr = sum(rhr_values) / len(rhr_values)
    min_rhr = min(rhr_values)
    max_rhr = max(rhr_values)
    
    # Add text box with statistics
    stats_text = (
        f"Days recorded: {len(dates)}\n"
        f"Average RHR: {avg_rhr:.1f} bpm\n"
        f"Min RHR: {min_rhr:.1f} bpm\n"
        f"Max RHR: {max_rhr:.1f} bpm"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Resting heart rate chart saved as '{output_file}'")
    plt.close()

def plot_rhr_histogram(data, output_dir='outputs'):
    """Create a histogram showing the distribution of resting heart rate values."""
    # Extract resting heart rate values
    rhr_values = [entry['resting_hr'] for entry in data]
    
    # Set output file
    output_file = os.path.join(output_dir, "resting_hr_histogram.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Create histogram
    bins = np.arange(min(rhr_values) - 1, max(rhr_values) + 3, 1)  # 1 bpm bins
    n, bins, patches = plt.hist(rhr_values, bins=bins, alpha=0.7, color='#3a7ebf')
    
    # Color the bins based on heart rate zones
    for i, p in enumerate(patches):
        if bins[i] < 60:
            p.set_facecolor('green')
        elif bins[i] < 70:
            p.set_facecolor('lightgreen')
        elif bins[i] < 80:
            p.set_facecolor('yellow')
        elif bins[i] < 90:
            p.set_facecolor('orange')
        else:
            p.set_facecolor('red')
    
    # Add vertical lines for heart rate zones
    plt.axvline(x=60, color='green', linestyle='--', alpha=0.5)
    plt.axvline(x=70, color='lightgreen', linestyle='--', alpha=0.5)
    plt.axvline(x=80, color='yellow', linestyle='--', alpha=0.5)
    plt.axvline(x=90, color='orange', linestyle='--', alpha=0.5)
    
    # Add text labels for zones
    plt.text(50, plt.ylim()[1]*0.95, 'Athletic (40-60)', 
             horizontalalignment='center', color='green')
    plt.text(65, plt.ylim()[1]*0.95, 'Good (60-70)', 
             horizontalalignment='center', color='darkgreen')
    plt.text(75, plt.ylim()[1]*0.95, 'Average (70-80)', 
             horizontalalignment='center', color='darkgoldenrod')
    plt.text(85, plt.ylim()[1]*0.95, 'Below Avg (80-90)', 
             horizontalalignment='center', color='darkorange')
    plt.text(95, plt.ylim()[1]*0.95, 'Poor (>90)', 
             horizontalalignment='center', color='darkred')
    
    # Configure axes
    plt.xlabel('Resting Heart Rate (bpm)')
    plt.ylabel('Frequency (Days)')
    plt.grid(True, alpha=0.3, axis='y')
    plt.title('Distribution of Resting Heart Rate Values')
    
    # Calculate statistics
    avg_rhr = sum(rhr_values) / len(rhr_values)
    median_rhr = sorted(rhr_values)[len(rhr_values)//2]
    
    # Add statistics annotation
    stats_text = (
        f"Total readings: {len(rhr_values)}\n"
        f"Mean RHR: {avg_rhr:.1f} bpm\n"
        f"Median RHR: {median_rhr:.1f} bpm\n"
        f"Range: {min(rhr_values):.1f} - {max(rhr_values):.1f} bpm"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Resting heart rate histogram saved as '{output_file}'")
    plt.close()

def plot_monthly_averages(data, output_dir='outputs'):
    """Create a chart showing average resting heart rate by month across all years."""
    from collections import defaultdict
    
    # Group by year and month
    monthly_data = defaultdict(list)
    
    for entry in data:
        date = entry['date']
        # Create a key in the format (year, month)
        key = (date.year, date.month)
        monthly_data[key].append(entry['resting_hr'])
    
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
    output_file = os.path.join(output_dir, "monthly_rhr_averages.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot monthly averages with colorization
    bars = plt.bar(range(len(avg_values)), avg_values)
    
    # Color bars based on RHR zones
    for i, bar in enumerate(bars):
        if avg_values[i] < 60:
            bar.set_color('green')
        elif avg_values[i] < 70:
            bar.set_color('lightgreen')
        elif avg_values[i] < 80:
            bar.set_color('yellow')
        elif avg_values[i] < 90:
            bar.set_color('orange')
        else:
            bar.set_color('red')
    
    # Add reference lines for heart rate zones
    plt.axhline(y=60, color='green', linestyle='--', alpha=0.3)
    plt.axhline(y=70, color='lightgreen', linestyle='--', alpha=0.3)
    plt.axhline(y=80, color='yellow', linestyle='--', alpha=0.3)
    plt.axhline(y=90, color='orange', linestyle='--', alpha=0.3)
    
    # Configure x-axis
    plt.xticks(range(len(avg_values)), month_labels, rotation=90)
    
    # Configure y-axis
    plt.ylabel('Average Resting Heart Rate (bpm)')
    
    # Add grid and title
    plt.grid(True, alpha=0.3, axis='y')
    plt.title('Average Monthly Resting Heart Rate')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Monthly RHR averages chart saved as '{output_file}'")
    plt.close()

if __name__ == "__main__":
    # Set directories
    DATA_DIR = 'data'
    OUTPUT_DIR = 'outputs'
    
    # Load data
    try:
        print("Starting chart generation process...")
        rhr_data = load_resting_hr_data(data_dir=DATA_DIR)
        
        # Ensure output directory exists
        ensure_dir(OUTPUT_DIR)
        print(f"All charts will be saved to the '{OUTPUT_DIR}' directory")
        
        # Create chart for all data
        print("\nGenerating chart for all years combined...")
        plot_resting_hr_chart(rhr_data, output_dir=OUTPUT_DIR)
        
        # Create histogram
        print("\nGenerating resting heart rate histogram...")
        plot_rhr_histogram(rhr_data, output_dir=OUTPUT_DIR)
        
        # Create monthly averages chart
        print("\nGenerating monthly averages chart...")
        plot_monthly_averages(rhr_data, output_dir=OUTPUT_DIR)
        
        # Group data by year
        print("\nGrouping data by year...")
        years_data = group_by_year(rhr_data)
        years = sorted(years_data.keys())
        print(f"Found data for years: {', '.join(map(str, years))}")
        
        # Create charts for each year
        for year in years:
            print(f"\nGenerating chart for year {year}...")
            year_data = years_data[year]
            
            # Only create charts if there's enough data (more than 30 days)
            if len(year_data) >= 30:
                plot_resting_hr_chart(year_data, year, output_dir=OUTPUT_DIR)
            else:
                print(f"Skipping year {year} - not enough data (only {len(year_data)} days)")
        
        print(f"\nAll charts saved to '{OUTPUT_DIR}/' directory")
        print("Charts generated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")