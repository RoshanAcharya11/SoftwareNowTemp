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
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data.extend(list(reader))
    return data

def main():
    """Execute temperature analysis."""
    try:
        data = read_csv_files()
        print(f"Read {len(data)} station records.")
        # TODO: Validate data, add analysis functions
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
