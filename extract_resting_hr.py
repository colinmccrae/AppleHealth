#!/usr/bin/env python3
"""
Extracts resting heart rate data from Apple Health export.xml file
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

def get_resting_hr_records(xml_path):
    """Extract resting heart rate records from Apple Health export."""
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print("Extracting resting heart rate records...")
    rhr_records = []
    
    for record in root.findall(".//Record[@type='HKQuantityTypeIdentifierRestingHeartRate']"):
        try:
            # Get record attributes
            value = float(record.get('value', 0))
            start_date = parse_datetime(record.get('startDate'))
            end_date = parse_datetime(record.get('endDate'))
            unit = record.get('unit', 'count/min')
            source = record.get('sourceName', 'Unknown')
            
            # Skip records with no or invalid value
            if value <= 0 or value > 200:  # Filter unlikely heart rates
                continue
                
            # Create record object
            rhr_records.append({
                'start_date': start_date,
                'end_date': end_date,
                'value': value,
                'unit': unit,
                'source': source,
                'date': start_date.date()  # For daily aggregation
            })
            
        except (ValueError, TypeError) as e:
            print(f"Error processing resting heart rate record: {e}")
    
    print(f"Found {len(rhr_records)} resting heart rate records")
    return rhr_records

def aggregate_by_day(records):
    """Aggregate resting heart rate records by day."""
    from collections import defaultdict
    import statistics
    
    # Dictionary to store data by day
    days = defaultdict(lambda: {
        'values': [],
        'sources': set()
    })
    
    for record in records:
        date = record['date']
        value = record['value']
        source = record['source']
        
        days[date]['values'].append(value)
        days[date]['sources'].add(source)
    
    # Calculate daily average
    result = []
    for date, data in days.items():
        values = data['values']
        # If multiple readings in a day, use their mean
        if len(values) > 0:
            result.append({
                'date': date,
                'resting_hr': round(statistics.mean(values), 1),
                'min_hr': min(values),
                'max_hr': max(values),
                'readings': len(values),
                'sources': data['sources']
            })
    
    # Sort by date
    result.sort(key=lambda x: x['date'])
    
    return result

def save_to_json(data, output_dir='data', filename='resting_hr_data.json'):
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
    """Calculate some basic statistics on the resting heart rate data."""
    if not data:
        return {}
    
    # Calculate average, min, max
    values = [entry['resting_hr'] for entry in data]
    count = len(values)
    average = sum(values) / count if count > 0 else 0
    minimum = min(values) if values else 0
    maximum = max(values) if values else 0
    
    # Find date with minimum and maximum values
    min_date = next((entry['date'] for entry in data if entry['resting_hr'] == minimum), None)
    max_date = next((entry['date'] for entry in data if entry['resting_hr'] == maximum), None)
    
    # Return statistics
    return {
        'days_recorded': count,
        'average_rhr': average,
        'min_rhr': minimum,
        'min_date': min_date,
        'max_rhr': maximum,
        'max_date': max_date
    }

if __name__ == "__main__":
    xml_path = "apple_health_export/export.xml"
    data_dir = "data"
    
    try:
        print(f"Will save output data to '{data_dir}/' directory")
        
        # Extract resting heart rate records
        rhr_records = get_resting_hr_records(xml_path)
        
        # Aggregate by day
        daily_data = aggregate_by_day(rhr_records)
        
        # Calculate stats
        stats = calculate_stats(daily_data)
        
        # Print statistics
        print("\nResting Heart Rate Statistics:")
        print(f"  Total days recorded: {stats['days_recorded']}")
        print(f"  Average resting heart rate: {stats['average_rhr']:.1f} bpm")
        print(f"  Minimum resting heart rate: {stats['min_rhr']:.1f} bpm on {stats['min_date']}")
        print(f"  Maximum resting heart rate: {stats['max_rhr']:.1f} bpm on {stats['max_date']}")
        
        # Save to JSON
        output_path = save_to_json(daily_data, output_dir=data_dir)
        
        print(f"Extraction complete. Data saved to {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")