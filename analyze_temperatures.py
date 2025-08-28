import os
import csv
import statistics
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
    """Calculate seasonal averages, largest range, and stability; write to files."""
    season_sums = defaultdict(float)
    season_counts = defaultdict(int)
    station_temps = defaultdict(list)
    
    for row in data:
        station = row['STATION_NAME']
        for month in SEASONS.values():
            for m in month:
                temp = row.get(m)
                if temp is not None:
                    season_sums[month] += temp
                    season_counts[month] += 1
                    station_temps[station].append(temp)
    
    # Seasonal averages
    season_averages = {s: season_sums[s] / season_counts[s] if season_counts[s] else 0.0 for s in SEASONS}
    with open('average_temp.txt', 'w', encoding='utf-8') as f:
        for season, avg in season_averages.items():
            f.write(f"{season}: {avg:.1f}°C\n")
    
    # Temperature range and stability
    station_stats = {
        s: {'range': max(temps) - min(temps), 'max': max(temps), 'min': min(temps), 
            'stddev': statistics.stdev(temps) if len(temps) > 1 else 0.0}
        for s, temps in station_temps.items() if temps
    }
    if not station_stats:
        raise ValueError("No valid temperature data.")
    
    # Largest range
    max_range = max(station_stats.values(), key=lambda x: x['range'])['range']
    with open('largest_temp_range_station.txt', 'w', encoding='utf-8') as f:
        for station, stats in station_stats.items():
            if abs(stats['range'] - max_range) < 0.0001:
                f.write(f"Station {station}: Range {stats['range']:.1f}°C (Max: {stats['max']:.1f}°C, Min: {stats['min']:.1f}°C)\n")
    
    # Temperature stability
    min_stddev = min(s['stddev'] for s in station_stats.values())
    max_stddev = max(s['stddev'] for s in station_stats.values())
    with open('temperature_stability_stations.txt', 'w', encoding='utf-8') as f:
        for station, stats in station_stats.items():
            if abs(stats['stddev'] - min_stddev) < 0.0001:
                f.write(f"Most Stable: {station}: StdDev {stats['stddev']:.1f}°C\n")
        for station, stats in station_stats.items():
            if abs(stats['stddev'] - max_stddev) < 0.0001:
                f.write(f"Most Variable: {station}: StdDev {stats['stddev']:.1f}°C\n")
    
    return season_averages, [(s, stats['range']) for s, stats in station_stats.items() if abs(stats['range'] - max_range) < 0.0001], \
           [(s, stats['stddev']) for s, stats in station_stats.items() if abs(stats['stddev'] - min_stddev) < 0.0001], \
           [(s, stats['stddev']) for s, stats in station_stats.items() if abs(stats['stddev'] - max_stddev) < 0.0001]

def main():
    """Execute temperature analysis."""
    try:
        data = read_csv_files()
        season_averages, max_range, most_stable, most_variable = analyze_temperatures(data)
        print(f"Seasonal averages: {season_averages}")
        print(f"Max range stations: {max_range}")
        print(f"Most stable: {most_stable}")
        print(f"Most variable: {most_variable}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
