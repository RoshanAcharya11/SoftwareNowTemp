import os
import csv
from collections import defaultdict

# Define Australian seasons
SEASONS = {
    'Summer': ['December', 'January', 'February'],
    'Autumn': ['March', 'April', 'May'],
    'Winter': ['June', 'July', 'August'],
    'Spring': ['September', 'October', 'November']
}

def read_csv_files(folder_path="temperatures"):
    """Read all CSV files and return combined data."""
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")
    data = []
    months = sum(SEASONS.values(), [])
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                if not all(col in reader.fieldnames for col in ['STATION_NAME'] + months):
                    continue
                data.extend([{month: float(row[month]) if row[month] else None for month in months} | 
                            {'STATION_NAME': row['STATION_NAME']} for row in reader])
    if not data:
        raise ValueError("No valid data found.")
    return data

def analyze_temperatures(data):
    """Calculate seasonal averages, collect per-station temperatures, and compute range."""
    season_sums = defaultdict(float)
    season_counts = defaultdict(int)
    station_temps = defaultdict(list)
    
    for row in data:
        station = row['STATION_NAME']
        for season, months in SEASONS.items():
            for m in months:
                temp = row.get(m)
                if temp is not None:
                    season_sums[season] += temp
                    season_counts[season] += 1
                    station_temps[station].append(temp)
    
    # Seasonal averages
    season_averages = {s: season_sums[s] / season_counts[s] if season_counts[s] else 0.0 for s in SEASONS}
    with open('average_temp.txt', 'w', encoding='utf-8') as f:
        for season, avg in season_averages.items():
            f.write(f"{season}: {avg:.1f}°C\n")
    
    # Compute temperature range
    station_stats = {
        s: {'range': max(temps) - min(temps), 'max': max(temps), 'min': min(temps)}
        for s, temps in station_temps.items() if temps
    }
    if not station_stats:
        raise ValueError("No valid temperature data.")
    max_range = max(station_stats.values(), key=lambda x: x['range'])['range']
    
    # TODO: Add range output
    # TODO: Calculate temperature stability
    return season_averages, max_range, station_stats

def main():
    """Execute temperature analysis."""
    try:
        data = read_csv_files()
        season_averages, max_range, station_stats = analyze_temperatures(data)
        print(f"Seasonal averages: {season_averages}")
        print(f"Max range: {max_range}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
