#!/usr/bin/env python3
"""
Extracts walking and running distance data from Apple Health export.xml file
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

def get_distance_records(xml_path):
    """Extract walking/running distance records from Apple Health export."""
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print("Extracting walking/running distance records...")
    distance_records = []
    
    for record in root.findall(".//Record[@type='HKQuantityTypeIdentifierDistanceWalkingRunning']"):
        try:
            # Get record attributes
            value = float(record.get('value', 0))
            unit = record.get('unit', 'km')
            start_date = parse_datetime(record.get('startDate'))
            end_date = parse_datetime(record.get('endDate'))
            source = record.get('sourceName', 'Unknown')
            
            # Convert to kilometers if in miles
            if unit == 'mi':
                value = value * 1.60934
                unit = 'km'
            
            # Skip records with no or invalid value
            if value <= 0:
                continue
                
            # Create record object
            distance_records.append({
                'start_date': start_date,
                'end_date': end_date,
                'value': value,
                'unit': unit,
                'source': source,
                'date': start_date.date()  # For daily aggregation
            })
            
        except (ValueError, TypeError) as e:
            print(f"Error processing distance record: {e}")
    
    print(f"Found {len(distance_records)} walking/running distance records")
    return distance_records

def aggregate_by_day(records):
    """Aggregate distance records by day."""
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
    result = [{'date': date, 'distance_km': round(data['total'], 2), 'sources': data['sources']} 
              for date, data in days.items()]
    result.sort(key=lambda x: x['date'])
    
    return result

def save_to_json(data, output_dir='data', filename='distance_data.json'):
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
    """Calculate some basic statistics on the distance data."""
    if not data:
        return {}
    
    # Calculate total, average, min, max
    values = [entry['distance_km'] for entry in data]
    count = len(values)
    total = sum(values)
    average = total / count if count > 0 else 0
    minimum = min(values) if values else 0
    maximum = max(values) if values else 0
    
    # Find date with minimum and maximum values
    min_date = next((entry['date'] for entry in data if entry['distance_km'] == minimum), None)
    max_date = next((entry['date'] for entry in data if entry['distance_km'] == maximum), None)
    
    # Calculate days with significant distance (e.g., > 5 km)
    days_over_5km = sum(1 for v in values if v >= 5)
    days_over_10km = sum(1 for v in values if v >= 10)
    
    # Return statistics
    return {
        'days_recorded': count,
        'total_distance_km': total,
        'average_daily_distance_km': average,
        'min_distance_km': minimum,
        'min_date': min_date,
        'max_distance_km': maximum,
        'max_date': max_date,
        'days_over_5km': days_over_5km,
        'days_over_10km': days_over_10km
    }

if __name__ == "__main__":
    xml_path = "apple_health_export/export.xml"
    data_dir = "data"
    
    try:
        print(f"Will save output data to '{data_dir}/' directory")
        
        # Extract distance records
        distance_records = get_distance_records(xml_path)
        
        # Aggregate by day
        daily_data = aggregate_by_day(distance_records)
        
        # Calculate stats
        stats = calculate_stats(daily_data)
        
        # Print statistics
        print("\nWalking/Running Distance Statistics:")
        print(f"  Total days recorded: {stats['days_recorded']}")
        print(f"  Total distance: {stats['total_distance_km']:.2f} km")
        print(f"  Average daily distance: {stats['average_daily_distance_km']:.2f} km")
        print(f"  Minimum distance: {stats['min_distance_km']:.2f} km on {stats['min_date']}")
        print(f"  Maximum distance: {stats['max_distance_km']:.2f} km on {stats['max_date']}")
        print(f"  Days with >5km: {stats['days_over_5km']} ({stats['days_over_5km']/stats['days_recorded']*100:.1f}%)")
        print(f"  Days with >10km: {stats['days_over_10km']} ({stats['days_over_10km']/stats['days_recorded']*100:.1f}%)")
        
        # Save to JSON
        output_path = save_to_json(daily_data, output_dir=data_dir)
        
        print(f"Extraction complete. Data saved to {output_path}")
        
    except Exception as e:
        print(f"An error occurred: {e}")