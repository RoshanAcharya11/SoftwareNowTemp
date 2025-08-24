import os
import csv

# Define Australian seasons
SEASONS = {
    'Summer': ['December', 'January', 'February'],
    'Autumn': ['March', 'April', 'May'],
    'Winter': ['June', 'July', 'August'],
    'Spring': ['September', 'October', 'November']
}

def read_csv_files(folder_path="temperatures"):
    """Read CSV files from the specified folder."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")
    data = []
    months = sum (SEASONS.values(), [])
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if not all(col in reader.fieldnames for col in ['STATION_NAME'] + months):
                    continue
                data.extend([{month: float(row[month]) if row [month] else None for month in months} | {'STATION_NAME' : row['STATION_NAME']} for row in reader])
    if not data:
        raise ValueError("No Valid data found.")
    return data
    
def analyze_temperatures(data):
    return

def main():
    """Execute temperature analysis."""
    try:
        data = read_csv_files()
        results = analyze_temperatures(data)
        print(f"Read {len(data)} station records.")
        # TODO: Validate data, add analysis functions
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

