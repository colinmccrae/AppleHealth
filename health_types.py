import xml.etree.ElementTree as ET

# Load and parse the XML file.
# (Optional): Load and parse the export_cda.xml file.
xml_path = "apple_health_export/export.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

# Create a set to store unique @type values.
types_set = set()

# Iterate through the XML elements and extract @type attribute.
for record in root.findall('.//Record'):
    type_attribute = record.get('type')
    if type_attribute:
        types_set.add(type_attribute)

# Define output file path
output_file = "health_types.txt"

# Write to file
with open(output_file, "w", encoding="utf-8") as file:
    for type_value in sorted(types_set):  # Sort for better readability
        print(type_value)  # Print to console
        file.write(type_value + "\n")  # Write to file

print(f"Unique types written to {output_file}")