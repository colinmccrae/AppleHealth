import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import json
import os

def parse_datetime(date_str):
    """Parse Apple Health date string into datetime object."""
    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S %z')

def get_sleep_records(xml_path):
    """Extract sleep analysis records from Apple Health export."""
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print("Extracting sleep records...")
    sleep_records = []
    
    for record in root.findall(".//Record[@type='HKCategoryTypeIdentifierSleepAnalysis']"):
        try:
            # Get record attributes
            value = record.get('value')
            start_date = parse_datetime(record.get('startDate'))
            end_date = parse_datetime(record.get('endDate'))
            source = record.get('sourceName', 'Unknown')
            
            # Calculate duration in hours
            duration = (end_date - start_date).total_seconds() / 3600
            
            # Skip extremely short or long durations (likely errors)
            if duration < 0.1 or duration > 24:
                continue
                
            # Create a date string for the night (using the start date)
            # If sleep starts before 6pm, it's likely a nap rather than night sleep
            is_nap = start_date.hour < 18 and start_date.hour > 8
            
            # Get date for the "night" (the previous day if sleep started after midnight)
            night_date = start_date.date()
            if start_date.hour < 6:
                night_date = (start_date - timedelta(days=1)).date()
            
            sleep_records.append({
                'start_date': start_date,
                'end_date': end_date,
                'duration': duration,
                'value': value,
                'source': source,
                'night_date': night_date,
                'is_nap': is_nap
            })
            
        except (ValueError, TypeError) as e:
            print(f"Error processing sleep record: {e}")
    
    print(f"Found {len(sleep_records)} sleep records")
    return sleep_records

def aggregate_sleep_by_night(sleep_records):
    """Aggregate sleep records by night and sleep type."""
    from collections import defaultdict
    
    # Dictionary to store sleep data by night
    nights = defaultdict(lambda: {
        'asleep': 0,
        'in_bed': 0,
        'unspecified': 0,
        'total': 0,
        'sources': set()
    })
    
    for record in sleep_records:
        night = record['night_date']
        duration = record['duration']
        value = record['value']
        source = record['source']
        
        # Skip naps for night sleep analysis
        if record['is_nap']:
            continue
            
        nights[night]['sources'].add(source)
        
        # Categorize by sleep type
        if 'Asleep' in value:
            nights[night]['asleep'] += duration
        elif 'InBed' in value:
            nights[night]['in_bed'] += duration
        else:
            nights[night]['unspecified'] += duration
            
        # Add to total regardless of type
        nights[night]['total'] += duration
    
    # Convert to list and sort by date
    result = [{'date': date, **data} for date, data in nights.items()]
    result.sort(key=lambda x: x['date'])
    
    return result

def ensure_dir(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    return directory

def save_sleep_data_json(sleep_data, output_dir='data', filename='sleep_data.json'):
    """Save processed sleep data to JSON file in the specified directory."""
    # Ensure the output directory exists
    ensure_dir(output_dir)
    
    # Build the full output path
    output_path = os.path.join(output_dir, filename)
    
    # Convert date objects and sets to strings for JSON serialization
    serializable_data = []
    for entry in sleep_data:
        serializable_entry = entry.copy()
        serializable_entry['date'] = str(entry['date'])
        serializable_entry['sources'] = list(entry['sources'])
        serializable_data.append(serializable_entry)
        
    with open(output_path, 'w') as f:
        json.dump(serializable_data, f, indent=2)
    
    print(f"Data saved as '{output_path}'")
    return output_path

if __name__ == "__main__":
    xml_path = "apple_health_export/export.xml"
    data_dir = "data"
    
    try:
        print(f"Will save output data to '{data_dir}/' directory")
        
        # Extract sleep records
        sleep_records = get_sleep_records(xml_path)
        
        # Aggregate by night
        sleep_data = aggregate_sleep_by_night(sleep_records)
        
        # Save to JSON in the data directory
        output_path = save_sleep_data_json(sleep_data, output_dir=data_dir)
        
        print(f"Extraction complete. You can now run visualize_sleep_charts.py to generate charts.")
        
    except Exception as e:
        print(f"An error occurred: {e}")