import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime
import json
import os

def load_sleep_data(data_dir='data', filename='sleep_data.json'):
    """Load sleep data from JSON file in the specified directory."""
    json_path = os.path.join(data_dir, filename)
    
    # Check if file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Data file not found at '{json_path}'. Please run extract_sleep_data.py first.")
    
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

def group_by_year(sleep_data):
    """Group sleep data by year."""
    years_data = {}
    
    for entry in sleep_data:
        year = entry['date'].year
        if year not in years_data:
            years_data[year] = []
        years_data[year].append(entry)
    
    return years_data

def ensure_output_dir(output_dir='outputs'):
    """Ensure the output directory exists."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    return output_dir

def plot_asleep_chart(sleep_data, year=None, output_file=None, output_dir='outputs'):
    """Create visualization for time asleep."""
    # Extract dates and sleep durations
    dates = [entry['date'] for entry in sleep_data]
    asleep_hours = [entry['asleep'] for entry in sleep_data]
    
    # Ensure output directory exists
    ensure_output_dir(output_dir)
    
    # Set default output file if not provided
    if output_file is None:
        year_str = f"_{year}" if year else ""
        output_file = os.path.join(output_dir, f"asleep_chart{year_str}.png")
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Calculate moving average (7-day window)
    window_size = 7
    asleep_moving_avg = calculate_moving_average(asleep_hours, window_size)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Define colors
    asleep_color = '#3a7ebf'  # blue
    asleep_avg_color = '#e55934'  # orange-red
    
    # Create bar chart
    plt.bar(dates_mdates, asleep_hours, label='Asleep', color=asleep_color, alpha=0.7)
    
    # Plot 7-day moving average
    plt.plot(dates_mdates, asleep_moving_avg, color=asleep_avg_color, linewidth=2.5, 
             label=f'{window_size}-Day Moving Average')
    
    # Add reference lines for recommended sleep duration
    plt.axhline(y=7, color='#000000', linestyle='--', alpha=0.3, label='7 Hours')
    plt.axhline(y=8, color='#000000', linestyle='-', alpha=0.3, label='8 Hours')
    
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
    plt.ylim(0, 12)
    plt.ylabel('Hours Asleep')
    
    # Add grid, legend and title
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Set title based on year
    title = f"Time Asleep in {year}" if year else "Time Asleep Over All Years"
    plt.title(title)
    
    # Calculate statistics
    avg_asleep = sum(asleep_hours) / len(asleep_hours)
    
    # Add text box with statistics
    stats_text = (
        f"Nights recorded: {len(dates)}\n"
        f"Average time asleep: {avg_asleep:.2f} hours"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Asleep chart saved as '{output_file}'")
    plt.close()

def plot_in_bed_chart(sleep_data, year=None, output_file=None, output_dir='outputs'):
    """Create visualization for time in bed (not asleep)."""
    # Extract dates and sleep durations
    dates = [entry['date'] for entry in sleep_data]
    in_bed_hours = [entry['in_bed'] for entry in sleep_data]
    
    # Ensure output directory exists
    ensure_output_dir(output_dir)
    
    # Set default output file if not provided
    if output_file is None:
        year_str = f"_{year}" if year else ""
        output_file = os.path.join(output_dir, f"in_bed_chart{year_str}.png")
    
    # Convert dates to matplotlib dates
    dates_mdates = mdates.date2num(dates)
    
    # Calculate moving average (7-day window)
    window_size = 7
    in_bed_moving_avg = calculate_moving_average(in_bed_hours, window_size)
    
    # Create the plot
    plt.figure(figsize=(15, 8))
    
    # Define colors
    in_bed_color = '#a0c4e2'  # light blue
    in_bed_avg_color = '#d62728'  # red
    
    # Create bar chart
    plt.bar(dates_mdates, in_bed_hours, label='In Bed', color=in_bed_color, alpha=0.7)
    
    # Plot 7-day moving average
    plt.plot(dates_mdates, in_bed_moving_avg, color=in_bed_avg_color, linewidth=2.5, 
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
    plt.ylim(0, 4)  # Adjusted for in-bed time which is typically less
    plt.ylabel('Hours In Bed (not asleep)')
    
    # Add grid, legend and title
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper left')
    
    # Set title based on year
    title = f"Time In Bed (not asleep) in {year}" if year else "Time In Bed (not asleep) Over All Years"
    plt.title(title)
    
    # Calculate statistics
    avg_in_bed = sum(in_bed_hours) / len(in_bed_hours)
    
    # Add text box with statistics
    stats_text = (
        f"Nights recorded: {len(dates)}\n"
        f"Average time in bed (not asleep): {avg_in_bed:.2f} hours"
    )
    plt.figtext(0.15, 0.02, stats_text, fontsize=10, 
                bbox={'facecolor': 'white', 'alpha': 0.8, 'pad': 5})
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"In bed chart saved as '{output_file}'")
    plt.close()

if __name__ == "__main__":
    # Set directories
    DATA_DIR = 'data'
    OUTPUT_DIR = 'outputs'
    
    # Load data
    try:
        print("Starting chart generation process...")
        sleep_data = load_sleep_data(data_dir=DATA_DIR)
        
        # Ensure output directory exists
        ensure_output_dir(OUTPUT_DIR)
        print(f"All charts will be saved to the '{OUTPUT_DIR}' directory")
        
        # Create charts for all data
        print("\nGenerating charts for all years combined...")
        plot_asleep_chart(sleep_data, output_dir=OUTPUT_DIR)
        plot_in_bed_chart(sleep_data, output_dir=OUTPUT_DIR)
        
        # Group data by year
        print("\nGrouping data by year...")
        years_data = group_by_year(sleep_data)
        years = sorted(years_data.keys())
        print(f"Found data for years: {', '.join(map(str, years))}")
        
        # Create charts for each year
        for year in years:
            print(f"\nGenerating charts for year {year}...")
            year_data = years_data[year]
            
            # Only create charts if there's enough data (more than 30 days)
            if len(year_data) >= 30:
                plot_asleep_chart(year_data, year, output_dir=OUTPUT_DIR)
                plot_in_bed_chart(year_data, year, output_dir=OUTPUT_DIR)
            else:
                print(f"Skipping year {year} - not enough data (only {len(year_data)} days)")
        
        print(f"\nAll charts saved to '{OUTPUT_DIR}/' directory")
        print("Charts generated successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")