# Apple Health Data Analysis

A comprehensive toolkit for extracting, analyzing, and visualizing Apple Health data using Python.

## Overview

This project provides tools to work with data exported from Apple Health, allowing you to:
- Extract various health metrics from the Apple Health export.xml file
- Process and aggregate the data for analysis
- Create visualizations to identify trends and patterns in your health data
- Analyze multiple health metrics including steps, sleep, energy, heart rate, and distance

## Getting Started

### Prerequisites

- Python 3.x
- Required Python packages (install with `pip install -r requirements-base.txt`):
  - matplotlib
  - numpy

### Setup

1. **Export your Apple Health data from your iPhone**:
   - Open the Health app
   - Tap your profile picture in the top right
   - Scroll down and tap "Export All Health Data"
   - Send the exported zip file to your computer

2. **Prepare the data**:
   - Unzip the export file
   - Place the entire `apple_health_export` folder in the project root directory

3. **Set up the environment**:
   ```bash
   python -m venv applehealth-env
   source applehealth-env/bin/activate  # On Windows: applehealth-env\Scripts\activate
   pip install -r requirements-base.txt
   ```

## Usage

The project workflow consists of two main steps:
1. Extract data from the Apple Health export
2. Visualize the extracted data

### Available Health Metrics

This project supports analyzing the following health metrics:

| Health Metric | Description | Extraction Script | Visualization Script |
|---------------|-------------|-------------------|----------------------|
| Sleep | Time asleep and in bed | `extract_sleep_data.py` | `visualize_sleep_charts.py` |
| Step Count | Daily steps | `extract_step_count.py` | `visualize_step_count.py` |
| Active Energy | Calories burned | `extract_active_energy.py` | `visualize_active_energy.py` |
| Resting Heart Rate | Daily RHR | `extract_resting_hr.py` | `visualize_resting_hr.py` |
| Distance | Walking/Running distance | `extract_distance.py` | `visualize_distance.py` |

### Analyze XML Structure

If you want to explore what data is available in your Apple Health export:

```bash
python summarise_xml_data.py
```

This will create a `data/xml_data_summary.md` file with details about all available data types in your export.

### Extract and Visualize Data

For each health metric, follow these steps:

1. **Extract the data**
   ```bash
   python extract_<metric>.py
   ```

2. **Create visualizations**
   ```bash
   python visualize_<metric>.py
   ```

Example for step count data:
```bash
python extract_step_count.py
python visualize_step_count.py
```

### Output

- Extracted data is saved in the `data/` directory as JSON files
- Visualizations are saved in the `outputs/` directory as PNG files

## Visualization Features

Each visualization script creates multiple charts:
- Daily/nightly values with 7-day moving averages
- Yearly breakdowns
- Monthly averages
- Cumulative totals
- Statistical summaries
- Distribution histograms

## Project Structure

```
AppleHealth/
├── README.md                  # Project documentation
├── apple_health_export/       # Directory for your Apple Health export data
├── data/                      # Extracted and processed data (JSON)
├── outputs/                   # Generated charts and visualizations
├── applehealth-env/           # Python virtual environment
├── requirements-base.txt      # Python dependencies
├── summarise_xml_data.py      # Script to analyze XML structure
├── extract_*.py               # Data extraction scripts
└── visualize_*.py             # Data visualization scripts
```

## Contributing

Contributions are welcome! Feel free to add support for additional health metrics.

## License

This project is open-source and available under the MIT License.
