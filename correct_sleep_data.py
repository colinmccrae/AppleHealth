#!/usr/bin/env python3
"""
This script corrects the sleep data in data/sleep_data.json by adjusting the
'asleep' value for dates from 2024-11-20 onwards.

Correction applied:
- For dates >= 2024-11-20: "asleep" = "asleep" - "in_bed"

This resolves an issue where 'asleep' time incorrectly included 'in_bed' time 
after a certain date.
"""

import json
import os
from datetime import datetime
import copy

def ensure_dir(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    return directory

def load_sleep_data(data_dir='data', filename='sleep_data.json'):
    """Load sleep data from JSON file."""
    json_path = os.path.join(data_dir, filename)
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"Data file not found at '{json_path}'. Please run extract_sleep_data.py first.")
    
    print(f"Loading data from {json_path}")
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} sleep records")
    return data

def save_sleep_data(data, data_dir='data', filename='sleep_data_corrected.json', backup=True):
    """Save corrected sleep data to JSON file."""
    # Ensure data directory exists
    ensure_dir(data_dir)
    
    # Create full output path
    output_path = os.path.join(data_dir, filename)
    
    # Create backup if requested
    if backup and os.path.exists(os.path.join(data_dir, 'sleep_data.json')):
        backup_path = os.path.join(data_dir, 'sleep_data_backup.json')
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(os.path.join(data_dir, 'sleep_data.json'), backup_path)
            print(f"Created backup at {backup_path}")
        else:
            print(f"Backup file {backup_path} already exists, skipping backup")
    
    # Save corrected data
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Corrected data saved to {output_path}")
    return output_path

def correct_sleep_data(data, cutoff_date='2024-11-20'):
    """
    Correct sleep data by adjusting 'asleep' value for dates after the cutoff.
    For dates >= cutoff_date: 'asleep' = 'asleep' - 'in_bed'
    """
    # Parse cutoff date
    cutoff = datetime.fromisoformat(cutoff_date).date()
    
    # Create a deep copy to avoid modifying the original data
    corrected_data = copy.deepcopy(data)
    
    # Counts for reporting
    total_records = len(corrected_data)
    corrected_records = 0
    
    # Process each record
    for entry in corrected_data:
        # Convert date string to datetime.date
        date = datetime.fromisoformat(entry['date']).date()
        
        # Apply correction for dates on or after cutoff
        if date >= cutoff:
            # Store original values for reporting
            original_asleep = entry['asleep']
            
            # Apply correction: asleep = asleep - in_bed
            entry['asleep'] = max(0, original_asleep - entry['in_bed'])
            
            # For tracking
            corrected_records += 1
    
    print(f"Processed {total_records} records")
    print(f"Applied correction to {corrected_records} records (dates >= {cutoff_date})")
    
    return corrected_data

def analyze_corrections(original_data, corrected_data):
    """Analyze the changes made to the data."""
    cutoff_date = datetime.fromisoformat('2024-11-20').date()
    
    # Convert original data to dict for easier lookup
    original_dict = {datetime.fromisoformat(entry['date']).date(): entry 
                    for entry in original_data}
    
    # Counter for statistics
    affected_records = 0
    total_difference = 0
    
    # Find the affected records
    for entry in corrected_data:
        date = datetime.fromisoformat(entry['date']).date()
        
        if date >= cutoff_date:
            original_asleep = original_dict[date]['asleep']
            corrected_asleep = entry['asleep']
            
            if original_asleep != corrected_asleep:
                affected_records += 1
                difference = original_asleep - corrected_asleep
                total_difference += difference
    
    # Print analysis
    if affected_records > 0:
        avg_difference = total_difference / affected_records
        print(f"\nCorrection Analysis:")
        print(f"  - Affected records: {affected_records}")
        print(f"  - Average reduction in 'asleep' time: {avg_difference:.2f} hours")
        print(f"  - Total sleep time reduction: {total_difference:.2f} hours")
    else:
        print("\nNo records were affected by the correction.")

def update_original_file(corrected_data, data_dir='data'):
    """Replace the original sleep_data.json with corrected data."""
    original_path = os.path.join(data_dir, 'sleep_data.json')
    
    # Confirm before overwriting
    confirm = input("\nDo you want to update the original sleep_data.json file with the corrected data? (y/n): ")
    
    if confirm.lower() == 'y':
        with open(original_path, 'w') as f:
            json.dump(corrected_data, f, indent=2)
        print(f"Original file {original_path} has been updated with corrected data.")
    else:
        print(f"Original file {original_path} remains unchanged.")

if __name__ == "__main__":
    try:
        # Load the original sleep data
        original_data = load_sleep_data()
        
        # Apply corrections
        corrected_data = correct_sleep_data(original_data)
        
        # Analyze the corrections
        analyze_corrections(original_data, corrected_data)
        
        # Save corrected data to a new file
        save_sleep_data(corrected_data)
        
        # Ask if user wants to update the original file
        update_original_file(corrected_data)
        
        print("\nCorrection process completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")