#!/usr/bin/env python3
"""
Extracts daily active energy burned data from Apple Health export.xml file
and saves the aggregated data as JSON.
"""

import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json
import os

def ensure_dir(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    return directory

def parse_datetime(date_str):
    """Parse Apple Health date string into datetime object."""
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')

def get_active_energy_records(xml_path):
    """Extract active energy records from Apple Health export."""
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print("Extracting active energy records...")
    active_energy_records = []
    
    for record in root.findall(".//Record[@type='HKQuantityTypeIdentifierActiveEnergyBurned']"):
        try:
            # Get record attributes
            value = float(record.get('value', 0))
            start_date = parse_datetime(record.get('startDate'))
            end_date = parse_datetime(record.get('endDate'))
            unit = record.get('unit', 'kcal')
            source = record.get('sourceName', 'Unknown')
            
            # Skip records with no or invalid value
            if value <= 0:
                continue
                
            # Create record object
            active_energy_records.append({
                'start_date': start_date,
                'end_date': end_date,
                'value': value,
                'unit': unit,
                'source': source,
                'date': start_date.date()  # For daily aggregation
            })
            
        except (ValueError, TypeError) as e:
            print(f"Error processing active energy record: {e}")
    
    print(f"Found {len(active_energy_records)} active energy records")
    return active_energy_records

def aggregate_by_day(records):
    """Aggregate active energy records by day."""
    from collections import defaultdict
    
    # Dictionary to store data by day
    days = defaultdict(lambda: {
        'total': 0,
        'sources': set()
    })
    
    for record in records:
        date = record['date']
        value = record['value']
        source = record['source']
        
        days[date]['total'] += value
        days[date]['sources'].add(source)
    
    # Convert to list and sort by date
    result = [{'date': date, 'active_calories': data['total'], 'sources': data['sources']} 
              for date, data in days.items()]
    result.sort(key=lambda x: x['date'])
    
    return result

def save_to_json(data, output_dir='data', filename='active_energy_data.json'):
    """Save processed data to JSON file in the specified directory."""
    # Ensure the output directory exists
    ensure_dir(output_dir)
    
    # Build the full output path
    output_path = os.path.join(output_dir, filename)
    
    # Convert date objects and sets to strings for JSON serialization
    serializable_data = []
    for entry in data:
        serializable_entry = entry.copy()
        serializable_entry['date'] = str(entry['date'])
        serializable_entry['sources'] = list(entry['sources'])
        serializable_data.append(serializable_entry)
        
    with open(output_path, 'w') as f:
        json.dump(serializable_data, f, indent=2)
    
    print(f"Data saved as '{output_path}'")
    return output_path

def calculate_stats(data):
    """Calculate some basic statistics on the active energy data."""
    if not data:
        return {}
    
    # Calculate total, average, min, max
    values = [entry['active_calories'] for entry in data]
    count = len(values)
    total = sum(values)
    average = total / count if count > 0 else 0
    minimum = min(values) if values else 0
    maximum = max(values) if values else 0
    
    # Find date with minimum and maximum values
    min_date = next((entry['date'] for entry in data if entry['active_calories'] == minimum), None)
    max_date = next((entry['date'] for entry in data if entry['active_calories'] == maximum), None)
    
    # Return statistics
    return {
        'days_recorded': count,
        'total_active_calories': total,
        'average_daily_active_calories': average,
        'min_active_calories': minimum,
        'min_date': min_date,
        'max_active_calories': maximum,
        'max_date': max_date
    }

if __name__ == "__main__":
    xml_path = "apple_health_export/export.xml"
    data_dir = "data"
    
    try:
        print(f"Will save output data to '{data_dir}/' directory")
        
        # Extract active energy records
        active_energy_records = get_active_energy_records(xml_path)
        
        # Aggregate by day
        daily_data = aggregate_by_day(active_energy_records)
        
        # Calculate stats
        stats = calculate_stats(daily_data)
        
        # Print statistics
        print("\nActive Energy Statistics:")
        print(f"  Total days recorded: {stats['days_recorded']}")
        print(f"  Average daily active energy: {stats['average_daily_active_calories']:.2f} kcal")
        print(f"  Minimum active energy: {stats['min_active_calories']:.2f} kcal on {stats['min_date']}")
        print(f"  Maximum active energy: {stats['max_active_calories']:.2f} kcal on {stats['max_date']}")
        
        # Save to JSON
        output_path = save_to_json(daily_data, output_dir=data_dir)
        
        print(f"Extraction complete. Data saved to {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")