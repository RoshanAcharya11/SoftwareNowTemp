import os
import csv
import statistics
from collections import defaultdict
import logging

# Configure logging for debugging and error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define Australian seasons
SEASONS = {
    'Summer': ['December', 'January', 'February'],
    'Autumn': ['March', 'April', 'May'],
    'Winter': ['June', 'July', 'August'],
    'Spring': ['September', 'October', 'November']
}

def read_csv_files(folder_path="temperatures"):
    """Read all CSV files from the specified folder and return combined data."""
    if not os.path.exists(folder_path):
        logging.error(f"Folder '{folder_path}' does not exist.")
        raise FileNotFoundError(f"Folder '{folder_path}' does not exist.")
    
    all_data = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    required_columns = ['STATION_NAME'] + list(SEASONS['Summer']) + list(SEASONS['Autumn']) + \
                                      list(SEASONS['Winter']) + list(SEASONS['Spring'])
                    if not all(col in reader.fieldnames for col in required_columns):
                        logging.warning(f"File '{filename}' missing required columns. Skipping.")
                        continue
                    for row in reader:
                        for month in required_columns[1:]:
                            try:
                                row[month] = float(row[month]) if row[month] else None
                            except (ValueError, TypeError):
                                row[month] = None
                        all_data.append(row)
                logging.info(f"Successfully read file: {filename}")
            except Exception as e:
                logging.error(f"Error reading file '{filename}': {str(e)}")
    if not all_data:
        logging.error("No valid data found in CSV files.")
        raise ValueError("No valid data found in CSV files.")
    return all_data

def calculate_seasonal_averages(data):
    """Calculate average temperature for each season across all stations and years."""
    season_sums = defaultdict(float)
    season_counts = defaultdict(int)
    
    for row in data:
        for season, months in SEASONS.items():
            for month in months:
                temp = row.get(month)
                if temp is not None:
                    season_sums[season] += temp
                    season_counts[season] += 1
    
    season_averages = {}
    for season in SEASONS:
        if season_counts[season] == 0:
            logging.warning(f"No valid data for {season}.")
            season_averages[season] = 0.0
        else:
            season_averages[season] = season_sums[season] / season_counts[season]
    
    try:
        with open('average_temp.txt', 'w', encoding='utf-8') as f:
            for season, avg in season_averages.items():
                f.write(f"{season}: {avg:.1f}°C\n")
        logging.info("Seasonal averages written to 'average_temp.txt'.")
    except Exception as e:
        logging.error(f"Error writing to 'average_temp.txt': {str(e)}")
        raise
    
    return season_averages

def find_largest_temp_range(data):
    """Find station(s) with the largest temperature range."""
    station_temps = defaultdict(list)
    
    for row in data:
        station = row['STATION_NAME']
        for month in ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']:
            temp = row.get(month)
            if temp is not None:
                station_temps[station].append(temp)
    
    station_ranges = {}
    for station, temps in station_temps.items():
        if temps:
            max_temp = max(temps)
            min_temp = min(temps)
            station_ranges[station] = {
                'range': max_temp - min_temp,
                'max': max_temp,
                'min': min_temp
            }
    
    if not station_ranges:
        logging.error("No valid temperature data for range calculation.")
        raise ValueError("No valid temperature data for range calculation.")
    
    max_range = max(station_ranges.values(), key=lambda x: x['range'])['range']
    
    max_range_stations = [
        (station, info) for station, info in station_ranges.items()
        if abs(info['range'] - max_range) < 0.0001
    ]
    
    try:
        with open('largest_temp_range_station.txt', 'w', encoding='utf-8') as f:
            for station, info in max_range_stations:
                f.write(f"Station {station}: Range {info['range']:.1f}°C "
                       f"(Max: {info['max']:.1f}°C, Min: {info['min']:.1f}°C)\n")
        logging.info("Largest temperature ranges written to 'largest_temp_range_station.txt'.")
    except Exception as e:
        logging.error(f"Error writing to 'largest_temp_range_station.txt': {str(e)}")
        raise
    
    return max_range_stations

def find_temperature_stability(data):
    """Find stations with most stable (lowest std dev) and most variable (highest std dev) temperatures."""
    station_temps = defaultdict(list)
    
    for row in data:
        station = row['STATION_NAME']
        for month in ['January', 'February', 'March', 'April', 'May', 'June',
                     'July', 'August', 'September', 'October', 'November', 'December']:
            temp = row.get(month)
            if temp is not None:
                station_temps[station].append(temp)
    
    station_stddevs = {}
    for station, temps in station_temps.items():
        if len(temps) > 1:
            station_stddevs[station] = statistics.stdev(temps)
        else:
            station_stddevs[station] = 0.0
            logging.warning(f"Station {station} has insufficient data for standard deviation.")
    
    if not station_stddevs:
        logging.error("No valid data for stability calculation.")
        raise ValueError("No valid data for stability calculation.")
    
    min_stddev = min(station_stddevs.values())
    max_stddev = max(station_stddevs.values())
    
    most_stable = [
        (station, stddev) for station, stddev in station_stddevs.items()
        if abs(stddev - min_stddev) < 0.0001
    ]
    most_variable = [
        (station, stddev) for station, stddev in station_stddevs.items()
        if abs(stddev - max_stddev) < 0.0001
    ]
    
    try:
        with open('temperature_stability_stations.txt', 'w', encoding='utf-8') as f:
            for station, stddev in most_stable:
                f.write(f"Most Stable: {station}: StdDev {stddev:.1f}°C\n")
            for station, stddev in most_variable:
                f.write(f"Most Variable: {station}: StdDev {stddev:.1f}°C\n")
        logging.info("Temperature stability results written to 'temperature_stability_stations.txt'.")
    except Exception as e:
        logging.error(f"Error writing to 'temperature_stability_stations.txt': {str(e)}")
        raise
    
    return most_stable, most_variable

def main():
    """Main function to execute the temperature analysis."""
    try:
        data = read_csv_files()
        seasonal_averages = calculate_seasonal_averages(data)
        logging.info(f"Seasonal averages: {seasonal_averages}")
        max_range_stations = find_largest_temp_range(data)
        logging.info(f"Stations with largest range: {[(s, info['range']) for s, info in max_range_stations]}")
        most_stable, most_variable = find_temperature_stability(data)
        logging.info(f"Most stable stations: {most_stable}")
        logging.info(f"Most variable stations: {most_variable}")
    except Exception as e:
        logging.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main()