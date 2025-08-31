import os
import csv
import statistics
from collections import defaultdict
import logging

# Set up logging to track execution and catch errors during processing
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define Australian seasons (Southern Hemisphere - December is summer start)
# Logic: Group months by seasonal patterns for meaningful temperature analysis
SEASONS = {
    'Summer': ['December', 'January', 'February'],  # Hottest months
    'Autumn': ['March', 'April', 'May'],            # Cooling transition
    'Winter': ['June', 'July', 'August'],           # Coldest months  
    'Spring': ['September', 'October', 'November']  # Warming transition
}

# Flatten all months into single list to avoid repetition in data processing
# Thinking: Rather than hardcode month lists 4 times, create once and reuse
ALL_MONTHS = [month for months in SEASONS.values() for month in months]

def read_csv_files(folder_path="temperatures"):
    """
    Read and validate CSV files, returning clean temperature data.
    
    Working Logic:
    1. Check if folder exists (fail fast if path is wrong)
    2. Find all CSV files in folder (filter by extension)
    3. For each CSV: validate columns, clean temperature data, collect rows
    4. Convert temperature strings to floats, handle empty/invalid values as None
    5. Return combined dataset from all valid CSV files
    
    Thinking: Batch process all CSVs to handle multi-file datasets efficiently
    """
    # Safety check: Ensure the data folder exists before attempting to read
    if not os.path.exists(folder_path):
        logging.error(f"Folder '{folder_path}' not found.")
        raise FileNotFoundError(f"Folder '{folder_path}' not found.")
    
    all_data = []
    # Filter for CSV files only (avoid processing non-CSV files accidentally)
    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    
    # Early exit if no CSV files found (common user error)
    if not csv_files:
        raise ValueError("No CSV files found in the specified folder.")
    
    # Process each CSV file individually to handle corrupted files gracefully
    for filename in csv_files:
        file_path = os.path.join(folder_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate CSV structure: Must have station name + all 12 months
                # Thinking: Better to skip bad files than crash entire analysis
                required_cols = ['STATION_NAME'] + ALL_MONTHS
                if not all(col in reader.fieldnames for col in required_cols):
                    logging.warning(f"'{filename}' missing required columns. Skipping.")
                    continue
                
                # Process each station record in the CSV
                for row in reader:
                    # Clean temperature data: convert strings to numbers, handle blanks
                    # Logic: Empty cells, spaces, or invalid values become None (missing data)
                    for month in ALL_MONTHS:
                        try:
                            row[month] = float(row[month]) if row[month].strip() else None
                        except (ValueError, AttributeError):
                            row[month] = None  # Invalid data treated as missing
                    all_data.append(row)
                    
            logging.info(f"Successfully processed: {filename}")
            
        except Exception as e:
            logging.error(f"Error reading '{filename}': {e}")
            # Continue processing other files even if one fails
    
    # Final validation: Ensure we have some valid data to work with
    if not all_data:
        raise ValueError("No valid temperature data found.")
    
    return all_data

def calculate_seasonal_averages(data):
    """
    Calculate and save seasonal temperature averages.
    
    Working Logic:
    1. Group all temperature values by season (across all stations/years)
    2. Calculate mean temperature for each season
    3. Save results to file for reference
    
    Thinking: Aggregate approach gives overall seasonal patterns rather than 
    per-station averages, which is more useful for climate analysis
    """
    # Collect temperature values grouped by season
    # Logic: Flatten all data points by season to get overall patterns
    season_data = defaultdict(list)
    
    for row in data:
        for season, months in SEASONS.items():
            # Extract valid temperatures for this season from current station
            temps = [row[month] for month in months if row[month] is not None]
            season_data[season].extend(temps)  # Add to running list for this season
    
    # Calculate average temperature per season
    # Thinking: Use mean of all data points, handle empty seasons gracefully
    season_averages = {
        season: statistics.mean(temps) if temps else 0.0 
        for season, temps in season_data.items()
    }
    
    # Persist results to file for external reference/reporting
    try:
        with open('average_temp.txt', 'w', encoding='utf-8') as f:
            for season, avg in season_averages.items():
                f.write(f"{season}: {avg:.1f}°C\n")
        logging.info("Seasonal averages saved to 'average_temp.txt'")
    except Exception as e:
        logging.error(f"Error writing seasonal averages: {e}")
        raise
    
    return season_averages

def find_largest_temp_range(data):
    """
    Find stations with the largest temperature range.
    
    Working Logic:
    1. Collect all temperature readings for each station
    2. Calculate range (max - min) for each station
    3. Find station(s) with the maximum range value
    4. Save detailed results showing range and extremes
    
    Thinking: Temperature range indicates climate variability - useful for 
    identifying continental vs coastal climate patterns
    """
    # Group all temperature readings by station name
    # Logic: Need all temps per station to find min/max across entire year
    station_temps = defaultdict(list)
    
    for row in data:
        station = row['STATION_NAME']
        # Collect all valid monthly temperatures for this station
        temps = [row[month] for month in ALL_MONTHS if row[month] is not None]
        station_temps[station].extend(temps)  # Accumulate across multiple years if present
    
    # Calculate temperature range (max - min) for each station
    # Thinking: Range shows climate variability - higher range = more extreme seasons
    station_ranges = {}
    for station, temps in station_temps.items():
        if temps:  # Only process stations with valid data
            station_ranges[station] = {
                'range': max(temps) - min(temps),  # Core metric: temperature variability
                'max': max(temps),                 # Hottest recorded temperature
                'min': min(temps)                  # Coldest recorded temperature
            }
    
    if not station_ranges:
        raise ValueError("No valid temperature data for range calculation.")
    
    # Find stations with maximum temperature range
    # Logic: Multiple stations might tie for largest range (within floating point precision)
    max_range = max(info['range'] for info in station_ranges.values())
    max_range_stations = [
        (station, info) for station, info in station_ranges.items()
        if abs(info['range'] - max_range) < 0.0001  # Handle floating point comparison
    ]
    
    # Save detailed results for external analysis
    try:
        with open('largest_temp_range_station.txt', 'w', encoding='utf-8') as f:
            for station, info in max_range_stations:
                f.write(f"Station {station}: Range {info['range']:.1f}°C "
                       f"(Max: {info['max']:.1f}°C, Min: {info['min']:.1f}°C)\n")
        logging.info("Temperature ranges saved to 'largest_temp_range_station.txt'")
    except Exception as e:
        logging.error(f"Error writing temperature ranges: {e}")
        raise
    
    return max_range_stations

def find_temperature_stability(data):
    """
    Find most stable and most variable temperature stations.
    
    Working Logic:
    1. Collect all temperature readings per station
    2. Calculate standard deviation for each station (measures variability)
    3. Find stations with lowest stddev (most stable/consistent climate)
    4. Find stations with highest stddev (most variable/unpredictable climate)
    5. Save both extremes for comparison
    
    Thinking: Standard deviation is the best metric for temperature consistency.
    Low stddev = steady climate, High stddev = extreme swings between hot/cold
    """
    # Accumulate all temperature readings by station
    # Logic: Need full temperature dataset per station to calculate meaningful stddev
    station_temps = defaultdict(list)
    
    for row in data:
        station = row['STATION_NAME']
        # Gather all valid monthly temperatures for this station
        temps = [row[month] for month in ALL_MONTHS if row[month] is not None]
        station_temps[station].extend(temps)  # Build complete temperature history
    
    # Calculate standard deviation for each station
    # Thinking: stddev measures how much temperatures vary from the mean
    # Higher stddev = more unpredictable/variable climate
    station_stddevs = {}
    for station, temps in station_temps.items():
        if len(temps) > 1:  # Need at least 2 data points for stddev calculation
            station_stddevs[station] = statistics.stdev(temps)
        else:
            # Handle edge case: stations with insufficient data
            station_stddevs[station] = 0.0
            logging.warning(f"Station {station} has insufficient data.")
    
    if not station_stddevs:
        raise ValueError("No valid data for stability calculation.")
    
    # Identify extremes: most stable (min stddev) and most variable (max stddev)
    # Logic: Multiple stations might tie, so find all stations matching min/max values
    min_stddev = min(station_stddevs.values())  # Most consistent temperatures
    max_stddev = max(station_stddevs.values())  # Most variable temperatures
    
    # Find all stations matching the extreme values (handle ties)
    # Thinking: Use small epsilon for floating point comparison precision
    most_stable = [(s, std) for s, std in station_stddevs.items() 
                   if abs(std - min_stddev) < 0.0001]
    most_variable = [(s, std) for s, std in station_stddevs.items() 
                     if abs(std - max_stddev) < 0.0001]
    
    # Save analysis results for external reporting/verification
    try:
        with open('temperature_stability_stations.txt', 'w', encoding='utf-8') as f:
            # Write most stable stations (predictable climate)
            for station, stddev in most_stable:
                f.write(f"Most Stable: {station}: StdDev {stddev:.1f}°C\n")
            # Write most variable stations (unpredictable climate)
            for station, stddev in most_variable:
                f.write(f"Most Variable: {station}: StdDev {stddev:.1f}°C\n")
        logging.info("Temperature stability results saved to 'temperature_stability_stations.txt'")
    except Exception as e:
        logging.error(f"Error writing stability results: {e}")
        raise
    
    return most_stable, most_variable

def main():
    """
    Execute temperature analysis with comprehensive error handling.
    
    Working Logic:
    1. Load and validate all CSV temperature data
    2. Run three separate analyses: seasonal averages, temperature ranges, stability
    3. Each analysis creates its own output file
    4. Log progress and handle failures gracefully
    
    Thinking: Orchestrate the full analysis pipeline while providing clear feedback
    to user about progress and any issues encountered
    """
    try:
        logging.info("Starting temperature analysis...")
        
        # Step 1: Load and validate all temperature data from CSV files
        # Logic: Fail early if data is missing or corrupted
        data = read_csv_files()
        logging.info(f"Loaded {len(data)} temperature records")
        
        # Step 2: Calculate overall seasonal temperature patterns
        # Thinking: Understanding seasonal trends is foundational for climate analysis
        seasonal_averages = calculate_seasonal_averages(data)
        logging.info("Seasonal averages calculated")
        
        # Step 3: Identify stations with extreme temperature variability
        # Logic: Range analysis reveals continental vs coastal climate characteristics
        max_range_stations = find_largest_temp_range(data)
        logging.info("Temperature ranges analyzed")
        
        # Step 4: Analyze temperature consistency patterns
        # Thinking: Stability analysis identifies predictable vs chaotic climate zones
        most_stable, most_variable = find_temperature_stability(data)
        logging.info("Temperature stability analyzed")
        
        # Provide user-friendly summary of completed analysis
        # Logic: Give immediate feedback about what was accomplished
        print("\n=== TEMPERATURE ANALYSIS COMPLETE ===")
        print(f"Processed {len(data)} records")
        print(f"Results saved to 3 output files")
        
    except Exception as e:
        # Handle any failures gracefully with clear error reporting
        # Thinking: Don't let the program crash silently - show what went wrong
        logging.error(f"Analysis failed: {e}")
        print(f"Error: {e}")
        raise

# Entry point: Only run analysis when script is executed directly
# Logic: Allows importing functions without auto-executing main analysis
if __name__ == "__main__":
    main() 

    #Final