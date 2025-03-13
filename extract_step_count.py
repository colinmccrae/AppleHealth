#!/usr/bin/env python3
"""
Extracts daily step count data from Apple Health export.xml file
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

def get_step_count_records(xml_path):
    """Extract step count records from Apple Health export."""
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print("Extracting step count records...")
    step_records = []
    
    for record in root.findall(".//Record[@type='HKQuantityTypeIdentifierStepCount']"):
        try:
            # Get record attributes
            value = int(float(record.get('value', 0)))
            start_date = parse_datetime(record.get('startDate'))
            end_date = parse_datetime(record.get('endDate'))
            unit = record.get('unit', 'count')
            source = record.get('sourceName', 'Unknown')
            
            # Skip records with no or invalid value
            if value <= 0:
                continue
                
            # Create record object
            step_records.append({
                'start_date': start_date,
                'end_date': end_date,
                'value': value,
                'unit': unit,
                'source': source,
                'date': start_date.date()  # For daily aggregation
            })
            
        except (ValueError, TypeError) as e:
            print(f"Error processing step count record: {e}")
    
    print(f"Found {len(step_records)} step count records")
    return step_records

def aggregate_by_day(records):
    """Aggregate step count records by day."""
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
    result = [{'date': date, 'steps': data['total'], 'sources': data['sources']} 
              for date, data in days.items()]
    result.sort(key=lambda x: x['date'])
    
    return result

def save_to_json(data, output_dir='data', filename='step_count_data.json'):
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
    """Calculate some basic statistics on the step count data."""
    if not data:
        return {}
    
    # Calculate total, average, min, max
    values = [entry['steps'] for entry in data]
    count = len(values)
    total = sum(values)
    average = total / count if count > 0 else 0
    minimum = min(values) if values else 0
    maximum = max(values) if values else 0
    
    # Find date with minimum and maximum values
    min_date = next((entry['date'] for entry in data if entry['steps'] == minimum), None)
    max_date = next((entry['date'] for entry in data if entry['steps'] == maximum), None)
    
    # Return statistics
    return {
        'days_recorded': count,
        'total_steps': total,
        'average_daily_steps': average,
        'min_steps': minimum,
        'min_date': min_date,
        'max_steps': maximum,
        'max_date': max_date
    }

if __name__ == "__main__":
    xml_path = "apple_health_export/export.xml"
    data_dir = "data"
    
    try:
        print(f"Will save output data to '{data_dir}/' directory")
        
        # Extract step count records
        step_records = get_step_count_records(xml_path)
        
        # Aggregate by day
        daily_data = aggregate_by_day(step_records)
        
        # Calculate stats
        stats = calculate_stats(daily_data)
        
        # Print statistics
        print("\nStep Count Statistics:")
        print(f"  Total days recorded: {stats['days_recorded']}")
        print(f"  Total steps: {stats['total_steps']:,}")
        print(f"  Average daily steps: {stats['average_daily_steps']:.1f}")
        print(f"  Minimum steps: {stats['min_steps']:,} on {stats['min_date']}")
        print(f"  Maximum steps: {stats['max_steps']:,} on {stats['max_date']}")
        
        # Save to JSON
        output_path = save_to_json(daily_data, output_dir=data_dir)
        
        print(f"Extraction complete. Data saved to {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")