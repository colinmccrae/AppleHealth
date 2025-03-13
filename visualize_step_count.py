#!/usr/bin/env python3
"""
Visualizes daily step count data from Apple Health.
Creates charts showing daily steps and trends over time.
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

def load_step_count_data(data_dir='data', filename='step_count_data.json'):
    """Load step count data from JSON file in the specified directory."""
    json_path = os.path.join(data_dir, filename)
    
    # Check if file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Data file not found at '{json_path}'. Please run extract_step_count.py first.")
    
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

def plot_step_count_chart(data, year=None, output_dir='outputs'):
    """Create visualization for daily step count."""
    # Extract dates and values
    dates = [entry['date'] for entry in data]
    steps = [entry['steps'] for entry in data]
    
    # Set default output file based on year
    year_str = f"_{year}" if year else ""
    output_file = os.path.join(output_dir, f"step_count_chart{year_str}.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Calculate moving average (7-day window)
    window_size = 7
    moving_avg = calculate_moving_average(steps, window_size)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Define colors
    bar_color = '#4CAF50'  # green
    line_color = '#3a7ebf'  # blue
    
    # Create bar chart
    plt.bar(dates_mdates, steps, label='Steps', color=bar_color, alpha=0.7)
    
    # Plot 7-day moving average
    plt.plot(dates_mdates, moving_avg, color=line_color, linewidth=2.5, 
             label=f'{window_size}-Day Moving Average')
    
    # Add reference lines for common step goals
    plt.axhline(y=10000, color='#e55934', linestyle='--', alpha=0.5, label='10,000 Steps Goal')
    
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
    max_steps = max(steps) * 1.1  # Add 10% headroom
    plt.ylim(0, max_steps)
    plt.ylabel('Steps')
    
    # Add grid, legend and title
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Set title based on year
    title = f"Daily Step Count in {year}" if year else "Daily Step Count Over All Years"
    plt.title(title)
    
    # Calculate statistics
    avg_steps = sum(steps) / len(steps)
    min_steps = min(steps)
    max_steps = max(steps)
    days_over_10k = sum(1 for s in steps if s >= 10000)
    percent_over_10k = (days_over_10k / len(steps)) * 100
    
    # Add text box with statistics
    stats_text = (
        f"Days recorded: {len(dates)}\n"
        f"Average steps: {avg_steps:.1f}\n"
        f"Min steps: {min_steps:,}\n"
        f"Max steps: {max_steps:,}\n"
        f"Days e 10K steps: {days_over_10k} ({percent_over_10k:.1f}%)"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Step count chart saved as '{output_file}'")
    plt.close()

def plot_cumulative_steps(data, output_dir='outputs'):
    """Create a visualization of cumulative step count over time."""
    # Extract dates and sort by date
    sorted_data = sorted(data, key=lambda x: x['date'])
    dates = [entry['date'] for entry in sorted_data]
    steps = [entry['steps'] for entry in sorted_data]
    
    # Calculate cumulative steps
    cumulative_steps = np.cumsum(steps)
    
    # Set output file
    output_file = os.path.join(output_dir, "cumulative_steps_chart.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot cumulative steps
    plt.plot(dates_mdates, cumulative_steps, color='#3a7ebf', linewidth=2.5)
    
    # Configure x-axis
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    plt.gcf().autofmt_xdate()
    
    # Configure y-axis
    plt.ylabel('Cumulative Steps')
    
    # Format y-axis labels with commas for thousands
    plt.gca().get_yaxis().set_major_formatter(
        plt.matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
    )
    
    # Add grid and title
    plt.grid(True, alpha=0.3)
    plt.title('Cumulative Step Count Over Time')
    
    # Calculate statistics
    total_steps = cumulative_steps[-1]
    total_days = len(dates)
    avg_daily = total_steps / total_days if total_days > 0 else 0
    
    # Add text box with statistics
    stats_text = (
        f"Total steps recorded: {total_steps:,}\n"
        f"Days recorded: {total_days}\n"
        f"Average steps per day: {avg_daily:.1f}"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Cumulative steps chart saved as '{output_file}'")
    plt.close()

def plot_monthly_averages(data, output_dir='outputs'):
    """Create a chart showing average steps by month across all years."""
    from collections import defaultdict
    
    # Group by year and month
    monthly_data = defaultdict(list)
    
    for entry in data:
        date = entry['date']
        # Create a key in the format (year, month)
        key = (date.year, date.month)
        monthly_data[key].append(entry['steps'])
    
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
    output_file = os.path.join(output_dir, "monthly_step_averages.png")
    
    # Ensure output directory exists
    ensure_dir(output_dir)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Plot monthly averages with colorization
    bars = plt.bar(range(len(avg_values)), avg_values)
    
    # Color bars based on average (red if below 7500, yellow if below 10000, green if above)
    for i, bar in enumerate(bars):
        if avg_values[i] < 7500:
            bar.set_color('#e55934')  # red
        elif avg_values[i] < 10000:
            bar.set_color('#ffa726')  # orange
        else:
            bar.set_color('#4CAF50')  # green
    
    # Add reference line for 10k goal
    plt.axhline(y=10000, color='#000000', linestyle='--', alpha=0.3, label='10,000 Steps Goal')
    
    # Configure x-axis
    plt.xticks(range(len(avg_values)), month_labels, rotation=90)
    
    # Configure y-axis
    plt.ylabel('Average Steps')
    
    # Add grid, legend, and title
    plt.grid(True, alpha=0.3, axis='y')
    plt.legend()
    plt.title('Average Daily Steps by Month')
    
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
        step_count_data = load_step_count_data(data_dir=DATA_DIR)
        
        # Ensure output directory exists
        ensure_dir(OUTPUT_DIR)
        print(f"All charts will be saved to the '{OUTPUT_DIR}' directory")
        
        # Create chart for all data
        print("\nGenerating chart for all years combined...")
        plot_step_count_chart(step_count_data, output_dir=OUTPUT_DIR)
        
        # Create cumulative steps chart
        print("\nGenerating cumulative steps chart...")
        plot_cumulative_steps(step_count_data, output_dir=OUTPUT_DIR)
        
        # Create monthly averages chart
        print("\nGenerating monthly averages chart...")
        plot_monthly_averages(step_count_data, output_dir=OUTPUT_DIR)
        
        # Group data by year
        print("\nGrouping data by year...")
        years_data = group_by_year(step_count_data)
        years = sorted(years_data.keys())
        print(f"Found data for years: {', '.join(map(str, years))}")
        
        # Create charts for each year
        for year in years:
            print(f"\nGenerating chart for year {year}...")
            year_data = years_data[year]
            
            # Only create charts if there's enough data (more than 30 days)
            if len(year_data) >= 30:
                plot_step_count_chart(year_data, year, output_dir=OUTPUT_DIR)
            else:
                print(f"Skipping year {year} - not enough data (only {len(year_data)} days)")
        
        print(f"\nAll charts saved to '{OUTPUT_DIR}/' directory")
        print("Charts generated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")