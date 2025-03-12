import xml.etree.ElementTree as ET

xml_path = "apple_health_export/export.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

records = []

for record in root.findall(".//Record[@type='HKCategoryTypeIdentifierSleepAnalysis']"):
    records.append({
        'start_date': record.get('startDate'),
        'end_date': record.get('endDate'),
        'value': record.get('value'),
        'unit': record.get('unit'),
    })

print(records[:1])