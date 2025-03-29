from flask import Flask, render_template, jsonify, request
import csv
import random
import uuid
from datetime import datetime
import os

app = Flask(__name__)

ORIGINS_CSV = 'origins.csv'
PATHS_CSV = 'paths.csv'

# --- Data (Should ideally be loaded from a separate file/db) ---
# Duplicated from main.js for now
AIRPORTS = [
    { "name": "JFK", "city": "New York", "state": "NY", "lat": 40.6413, "lng": -73.7781, "type": 'airport' },
    { "name": "LAX", "city": "Los Angeles", "state": "CA", "lat": 33.9416, "lng": -118.4085, "type": 'airport' },
    { "name": "ORD", "city": "Chicago", "state": "IL", "lat": 41.9742, "lng": -87.9073, "type": 'airport' },
    { "name": "ATL", "city": "Atlanta", "state": "GA", "lat": 33.6407, "lng": -84.4277, "type": 'airport' },
    { "name": "DFW", "city": "Dallas", "state": "TX", "lat": 32.8998, "lng": -97.0403, "type": 'airport' },
    { "name": "DEN", "city": "Denver", "state": "CO", "lat": 39.8561, "lng": -104.6737, "type": 'airport' },
    { "name": "SFO", "city": "San Francisco", "state": "CA", "lat": 37.6213, "lng": -122.3790, "type": 'airport' },
    { "name": "SEA", "city": "Seattle", "state": "WA", "lat": 47.4502, "lng": -122.3088, "type": 'airport' },
    { "name": "MIA", "city": "Miami", "state": "FL", "lat": 25.7959, "lng": -80.2871, "type": 'airport' },
    { "name": "BOS", "city": "Boston", "state": "MA", "lat": 42.3656, "lng": -71.0096, "type": 'airport' }
]

DISEASE_PREFIXES = ["Flu", "Virus", "Strain", "Pathogen", "Contagion", "Blight"]
DISEASE_SUFFIXES = ["Alpha", "Beta", "Gamma", "Delta", "Zeta", "Omega", "X", "Prime", "7", "9"]
DISEASE_COLORS = [
    '#FF0000', # Red
    '#0000FF', # Blue
    '#00FF00', # Lime Green
    '#FFFF00', # Yellow
    '#FF00FF', # Magenta
    '#00FFFF', # Cyan
    '#FFA500', # Orange
    '#800080', # Purple
    '#FFFFFF', # White (use carefully depending on background)
    '#008000', # Green
    '#FFC0CB', # Pink
    '#4682B4'  # Steel Blue
]

# --- Helper Functions ---

def get_airports():
    """Returns the list of airports."""
    return AIRPORTS

def generate_disease_name():
    """Generates a random disease name."""
    return f"{random.choice(DISEASE_PREFIXES)} {random.choice(DISEASE_SUFFIXES)}"

def generate_disease_color():
    """Selects a random color."""
    return random.choice(DISEASE_COLORS)

def log_to_csv(filename, data_row):
    """Appends a row to the specified CSV file. Creates header if file is new/empty."""
    is_new_file = not os.path.exists(filename) or os.path.getsize(filename) == 0
    # Use 'a+' to create file if it doesn't exist, and allow reading/writing
    # Use newline='' to prevent extra blank rows in CSV
    try:
        with open(filename, 'a+', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            if is_new_file:
                # Write header based on the keys of the first data row
                if filename == ORIGINS_CSV:
                    writer.writerow(["instance_id", "disease_name", "origin_airport", "timestamp"])
                elif filename == PATHS_CSV:
                    writer.writerow(['instance_id', 'timestamp', 'location_name', 'location_type', 'lat', 'lng'])
                else:
                    print(f"Warning: Unknown CSV filename for logging: {filename}")
            if data_row:
                writer.writerow(data_row.values())
    except IOError as e:
        print(f"Error writing to CSV {filename}: {e}")

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_outbreak', methods=['POST'])
def start_outbreak():
    """Starts a new disease outbreak instance."""
    airports = get_airports()
    if not airports:
        return jsonify({"error": "No airport data available"}), 500

    instance_id = str(uuid.uuid4())
    disease_name = generate_disease_name()
    disease_color = generate_disease_color()
    origin_airport = random.choice(airports)
    timestamp = datetime.now().isoformat()

    # Log to origins.csv
    origin_log = {
        "instance_id": instance_id,
        "disease_name": disease_name,
        "origin_airport": origin_airport['name'],
        "timestamp": timestamp
    }
    log_to_csv(ORIGINS_CSV, origin_log)

    # Log initial infection to paths.csv
    path_log = {
        "instance_id": instance_id,
        "timestamp": timestamp,
        "location_name": origin_airport['name'],
        "location_type": origin_airport['type'],
        "lat": origin_airport['lat'],
        "lng": origin_airport['lng']
    }
    log_to_csv(PATHS_CSV, path_log)

    # Return details to the frontend
    outbreak_details = {
        "instanceId": instance_id,
        "name": disease_name,
        "color": disease_color,
        "origin": origin_airport # Send the full origin airport data
    }
    return jsonify(outbreak_details)

@app.route('/api/log_step', methods=['POST'])
def log_step():
    """Logs a step in a disease's path to paths.csv."""
    data = request.json
    instance_id = data.get('instanceId')
    location_name = data.get('locationName')
    location_type = data.get('locationType')
    lat = data.get('lat')
    lng = data.get('lng')

    if not all([instance_id, location_name, location_type, lat is not None, lng is not None]):
        return jsonify({"status": "error", "message": "Missing data for logging step"}), 400

    log_entry = {
        'instance_id': instance_id,
        'timestamp': datetime.now().isoformat(),
        'location_name': location_name,
        'location_type': location_type,
        'lat': lat,
        'lng': lng
    }
    log_to_csv(PATHS_CSV, log_entry)

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True)
