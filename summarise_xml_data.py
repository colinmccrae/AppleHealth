import xml.etree.ElementTree as ET
from collections import defaultdict
import json
import os

def analyze_xml_structure(xml_path):
    print(f"Parsing {xml_path}...")
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    print("Analyzing XML structure...")
    # Dictionary to store information about each type of Record
    data_types = defaultdict(lambda: {
        'count': 0,
        'attributes': set(),
        'example': None,
        'date_range': {'start': None, 'end': None}
    })
    
    # Dictionary for other types of elements (not Record)
    element_types = defaultdict(lambda: {
        'count': 0,
        'attributes': set(),
        'children': set(),
        'example': None
    })
    
    # Process all elements in the XML
    for element in root.findall('.//*'):
        tag = element.tag
        
        # Handle Record elements specially
        if tag == 'Record':
            record_type = element.get('type')
            if record_type:
                # Increment count
                data_types[record_type]['count'] += 1
                
                # Collect all attributes
                for attr_name, attr_value in element.attrib.items():
                    data_types[record_type]['attributes'].add(attr_name)
                
                # Store first example
                if data_types[record_type]['example'] is None:
                    data_types[record_type]['example'] = dict(element.attrib)
                
                # Update date range if available
                start_date = element.get('startDate')
                if start_date:
                    if (data_types[record_type]['date_range']['start'] is None or 
                        start_date < data_types[record_type]['date_range']['start']):
                        data_types[record_type]['date_range']['start'] = start_date
                
                end_date = element.get('endDate')
                if end_date:
                    if (data_types[record_type]['date_range']['end'] is None or 
                        end_date > data_types[record_type]['date_range']['end']):
                        data_types[record_type]['date_range']['end'] = end_date
        else:
            # For non-Record elements
            element_types[tag]['count'] += 1
            
            # Collect attributes
            for attr_name, attr_value in element.attrib.items():
                element_types[tag]['attributes'].add(attr_name)
            
            # Collect child element tags
            for child in element:
                element_types[tag]['children'].add(child.tag)
            
            # Store first example
            if element_types[tag]['example'] is None and element.attrib:
                element_types[tag]['example'] = dict(element.attrib)
    
    return {
        'data_types': {k: {
            'count': v['count'],
            'attributes': list(v['attributes']),
            'example': v['example'],
            'date_range': v['date_range']
        } for k, v in data_types.items()},
        'element_types': {k: {
            'count': v['count'],
            'attributes': list(v['attributes']),
            'children': list(v['children']),
            'example': v['example']
        } for k, v in element_types.items()}
    }

def ensure_dir(directory):
    """Ensure a directory exists, creating it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory: {directory}")
    return directory

def format_output(structure):
    output = []
    
    # Add summary
    output.append("# XML DATA STRUCTURE SUMMARY")
    output.append("\n## Basic Structure")
    
    # Element types summary
    output.append("\n### Element Types")
    for elem_type, info in structure['element_types'].items():
        output.append(f"\n#### {elem_type} ({info['count']} elements)")
        if info['attributes']:
            output.append("  Attributes: " + ", ".join(info['attributes']))
        if info['children']:
            output.append("  Child elements: " + ", ".join(info['children']))
        if info['example']:
            output.append("  Example: " + json.dumps(info['example'], indent=2).replace('\n', '\n  '))
    
    # Data types summary (Records)
    output.append("\n## Health Data Types")
    for data_type, info in sorted(structure['data_types'].items()):
        output.append(f"\n### {data_type} ({info['count']} records)")
        if info['date_range']['start'] and info['date_range']['end']:
            output.append(f"  Date range: {info['date_range']['start']} to {info['date_range']['end']}")
        output.append("  Attributes: " + ", ".join(info['attributes']))
        if info['example']:
            output.append("  Example: " + json.dumps(info['example'], indent=2).replace('\n', '\n  '))
    
    return "\n".join(output)

if __name__ == "__main__":
    xml_path = "apple_health_export/export.xml"
    output_dir = "data"
    output_file = "xml_data_summary.md"
    
    try:
        # Ensure data directory exists
        ensure_dir(output_dir)
        
        # Create full output path
        output_path = os.path.join(output_dir, output_file)
        
        print(f"Will save output to {output_path}")
        
        # Analyze XML structure
        structure = analyze_xml_structure(xml_path)
        
        # Format the output text
        output_text = format_output(structure)
        
        # Write to the output file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_text)
        
        print(f"Structure analysis completed and saved to {output_path}")
    except Exception as e:
        print(f"An error occurred: {e}")