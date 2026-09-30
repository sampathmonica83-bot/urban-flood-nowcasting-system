from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

app = Flask(__name__)

DB_PATH = Path(__file__).with_name("flood.db")


# ---------------------------------------------------------
# DEMONSTRATION LOCATION DATA
# ---------------------------------------------------------

LOCATIONS = {
    "Chennai": {
        "country": "India",
        "lat": 13.0827,
        "lon": 80.2707,
        "rainfall": 42,
        "water": 1.8,
        "drainage": 68
    },

    "Mumbai": {
        "country": "India",
        "lat": 19.0760,
        "lon": 72.8777,
        "rainfall": 85,
        "water": 2.8,
        "drainage": 91
    },

    "Tokyo": {
        "country": "Japan",
        "lat": 35.6762,
        "lon": 139.6503,
        "rainfall": 45,
        "water": 1.4,
        "drainage": 61
    },

    "Singapore": {
        "country": "Singapore",
        "lat": 1.3521,
        "lon": 103.8198,
        "rainfall": 91,
        "water": 2.6,
        "drainage": 88
    },

    "Sydney": {
        "country": "Australia",
        "lat": -33.8688,
        "lon": 151.2093,
        "rainfall": 36,
        "water": 1.3,
        "drainage": 58
    },

    "London": {
        "country": "UK",
        "lat": 51.5074,
        "lon": -0.1278,
        "rainfall": 49,
        "water": 1.5,
        "drainage": 63
    },

    "Paris": {
        "country": "France",
        "lat": 48.8566,
        "lon": 2.3522,
        "rainfall": 43,
        "water": 1.4,
        "drainage": 59
    },

    "Berlin": {
        "country": "Germany",
        "lat": 52.5200,
        "lon": 13.4050,
        "rainfall": 38,
        "water": 1.2,
        "drainage": 55
    },

    "New York": {
        "country": "USA",
        "lat": 40.7128,
        "lon": -74.0060,
        "rainfall": 68,
        "water": 2.2,
        "drainage": 74
    },

    "Los Angeles": {
        "country": "USA",
        "lat": 34.0522,
        "lon": -118.2437,
        "rainfall": 22,
        "water": 0.7,
        "drainage": 41
    },

    "Toronto": {
        "country": "Canada",
        "lat": 43.6532,
        "lon": -79.3832,
        "rainfall": 45,
        "water": 1.4,
        "drainage": 61
    },

    "Mexico City": {
        "country": "Mexico",
        "lat": 19.4326,
        "lon": -99.1332,
        "rainfall": 72,
        "water": 2.3,
        "drainage": 79
    },

    "Rio de Janeiro": {
        "country": "Brazil",
        "lat": -22.9068,
        "lon": -43.1729,
        "rainfall": 89,
        "water": 2.7,
        "drainage": 86
    },

    "Buenos Aires": {
        "country": "Argentina",
        "lat": -34.6037,
        "lon": -58.3816,
        "rainfall": 51,
        "water": 1.7,
        "drainage": 67
    },

    "Dubai": {
        "country": "UAE",
        "lat": 25.2048,
        "lon": 55.2708,
        "rainfall": 18,
        "water": 0.6,
        "drainage": 35
    },

    "Cairo": {
        "country": "Egypt",
        "lat": 30.0444,
        "lon": 31.2357,
        "rainfall": 8,
        "water": 0.4,
        "drainage": 28
    },

    "Lagos": {
        "country": "Nigeria",
        "lat": 6.5244,
        "lon": 3.3792,
        "rainfall": 94,
        "water": 2.9,
        "drainage": 93
    },

    "Cape Town": {
        "country": "South Africa",
        "lat": -33.9249,
        "lon": 18.4241,
        "rainfall": 31,
        "water": 1.0,
        "drainage": 49
    },

    "Nairobi": {
        "country": "Kenya",
        "lat": -1.2921,
        "lon": 36.8219,
        "rainfall": 58,
        "water": 1.8,
        "drainage": 69
    },

    "Shanghai": {
        "country": "China",
        "lat": 31.2304,
        "lon": 121.4737,
        "rainfall": 82,
        "water": 2.6,
        "drainage": 87
    },

    "Beijing": {
        "country": "China",
        "lat": 39.9042,
        "lon": 116.4074,
        "rainfall": 57,
        "water": 1.9,
        "drainage": 71
    },

    "Seoul": {
        "country": "South Korea",
        "lat": 37.5665,
        "lon": 126.9780,
        "rainfall": 74,
        "water": 2.3,
        "drainage": 81
    },

    "Jakarta": {
        "country": "Indonesia",
        "lat": -6.2088,
        "lon": 106.8456,
        "rainfall": 97,
        "water": 3.0,
        "drainage": 95
    },

    "Manila": {
        "country": "Philippines",
        "lat": 14.5995,
        "lon": 120.9842,
        "rainfall": 88,
        "water": 2.8,
        "drainage": 91
    },

    "Bangkok": {
        "country": "Thailand",
        "lat": 13.7563,
        "lon": 100.5018,
        "rainfall": 84,
        "water": 2.5,
        "drainage": 86
    },

    "Kuala Lumpur": {
        "country": "Malaysia",
        "lat": 3.1390,
        "lon": 101.6869,
        "rainfall": 92,
        "water": 2.7,
        "drainage": 89
    },

    "Auckland": {
        "country": "New Zealand",
        "lat": -36.8509,
        "lon": 174.7645,
        "rainfall": 47,
        "water": 1.4,
        "drainage": 60
    },

    "Istanbul": {
        "country": "Türkiye",
        "lat": 41.0082,
        "lon": 28.9784,
        "rainfall": 52,
        "water": 1.7,
        "drainage": 64
    },

    "Moscow": {
        "country": "Russia",
        "lat": 55.7558,
        "lon": 37.6173,
        "rainfall": 34,
        "water": 1.1,
        "drainage": 52
    }
}


# ---------------------------------------------------------
# FLOOD RISK MODEL
# ---------------------------------------------------------

def calculate_risk(data):
    """
    Demonstration risk model.

    For a real deployment, this should be replaced with
    a calibrated hydrological/meteorological model.
    """

    risk = (
        (data["rainfall"] / 100) * 45
        + (data["water"] / 3) * 35
        + (data["drainage"] / 100) * 20
    )

    return max(0, min(100, round(risk)))


def risk_status(risk):

    if risk < 35:
        return "LOW"

    if risk < 65:
        return "MEDIUM"

    return "HIGH"


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

def init_db():

    with sqlite3.connect(DB_PATH) as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                location TEXT NOT NULL,
                issue TEXT NOT NULL,
                description TEXT NOT NULL,
                severity TEXT NOT NULL,
                reporter TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Received'
            )
        """)

        conn.commit()


# ---------------------------------------------------------
# MAIN PAGE
# ---------------------------------------------------------

@app.route("/")
def home():

    return render_template("index.html")


# ---------------------------------------------------------
# LOCATION API
# ---------------------------------------------------------

@app.get("/api/locations")
def get_locations():

    result = []

    for name, data in LOCATIONS.items():

        risk = calculate_risk(data)

        result.append({
            "name": name,
            "country": data["country"],
            "lat": data["lat"],
            "lon": data["lon"],
            "rainfall": data["rainfall"],
            "water": data["water"],
            "drainage": data["drainage"],
            "risk": risk,
            "status": risk_status(risk)
        })

    return jsonify(result)


# ---------------------------------------------------------
# GET COMPLAINTS
# ---------------------------------------------------------

@app.get("/api/complaints")
def get_complaints():

    with sqlite3.connect(DB_PATH) as conn:

        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT
                id,
                location,
                issue,
                description,
                severity,
                reporter,
                created_at,
                status
            FROM complaints
            ORDER BY id DESC
            LIMIT 100
        """).fetchall()

    return jsonify([dict(row) for row in rows])


# ---------------------------------------------------------
# CREATE COMPLAINT
# ---------------------------------------------------------

@app.post("/api/complaints")
def create_complaint():

    data = request.get_json(silent=True) or {}

    location = str(data.get("location", "")).strip()
    issue = str(data.get("issue", "")).strip()
    description = str(data.get("description", "")).strip()
    severity = str(data.get("severity", "Medium")).strip()
    reporter = str(data.get("reporter", "")).strip()

    if not location or not issue or not description:

        return jsonify({
            "error": "Location, issue and description are required."
        }), 400

    if len(description) > 1000:

        return jsonify({
            "error": "Description must be 1000 characters or fewer."
        }), 400

    allowed_severity = {
        "Low",
        "Medium",
        "High",
        "Critical"
    }

    if severity not in allowed_severity:
        severity = "Medium"

    created_at = datetime.now(
        timezone.utc
    ).isoformat(timespec="seconds")

    with sqlite3.connect(DB_PATH) as conn:

        cursor = conn.execute("""
            INSERT INTO complaints
            (
                location,
                issue,
                description,
                severity,
                reporter,
                created_at,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Received')
        """, (
            location,
            issue,
            description,
            severity,
            reporter,
            created_at
        ))

        complaint_id = cursor.lastrowid

        conn.commit()

    return jsonify({
        "message": "Complaint received successfully.",
        "complaint_id": complaint_id
    }), 201


# ---------------------------------------------------------
# START APPLICATION
# ---------------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(debug=True)