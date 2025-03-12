import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
from datetime import datetime

xml_path = "apple_health_export/export.xml"
tree = ET.parse(xml_path)
root = tree.getroot()

records = []

for record in root.findall(".//Record[@type='HKQuantityTypeIdentifierStepCount']"):
    start_date = record.get('startDate')
    value = int(record.get('value'))
    date_obj = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S %z')
    records.append((date_obj, value))

records.sort(key=lambda x: x[0])

dates = []
cumulative_steps = []
total_steps = 0

for record in records:
    date, steps = record
    total_steps += steps
    dates.append(date)
    cumulative_steps.append(total_steps)

plt.figure(figsize=(10, 6))
plt.plot(dates, cumulative_steps, linestyle='-', color='blue')
plt.xlabel('Date')
plt.ylabel('Cumulative Step Count')
plt.title('Cumulative Daily Step Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()