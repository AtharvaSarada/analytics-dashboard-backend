"""
Flask Analytics Dashboard API
Simple Flask application for the analytics dashboard backend.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os
import random

# Create Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Database file path
DB_PATH = "analytics.db"

def init_db():
    """Initialize SQLite database with sample data"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Check if we already have data
    cursor.execute("SELECT COUNT(*) FROM analytics_data")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Insert sample data
        sample_data = [
            ("revenue", 15420.50, "2024-01-15T10:00:00"),
            ("users", 342, "2024-01-15T10:00:00"),
            ("orders", 28, "2024-01-15T10:00:00"),
            ("conversion_rate", 8.2, "2024-01-15T10:00:00"),
            ("page_views", 1250, "2024-01-15T10:00:00"),
            ("bounce_rate", 45.3, "2024-01-15T10:00:00"),
            
            ("revenue", 16200.25, "2024-01-15T11:00:00"),
            ("users", 367, "2024-01-15T11:00:00"),
            ("orders", 31, "2024-01-15T11:00:00"),
            ("conversion_rate", 8.4, "2024-01-15T11:00:00"),
            ("page_views", 1380, "2024-01-15T11:00:00"),
            ("bounce_rate", 43.1, "2024-01-15T11:00:00"),
            
            ("revenue", 17100.75, "2024-01-15T12:00:00"),
            ("users", 389, "2024-01-15T12:00:00"),
            ("orders", 35, "2024-01-15T12:00:00"),
            ("conversion_rate", 9.0, "2024-01-15T12:00:00"),
            ("page_views", 1420, "2024-01-15T12:00:00"),
            ("bounce_rate", 41.8, "2024-01-15T12:00:00"),
        ]
        
        cursor.executemany(
            "INSERT INTO analytics_data (metric_name, value, timestamp) VALUES (?, ?, ?)",
            sample_data
        )
        
        print("Sample data inserted into database")
    
    conn.commit()
    conn.close()

@app.route('/')
def root():
    """Root endpoint"""
    return jsonify({
        "message": "Real-time Analytics Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "health": "/health",
            "summary": "/api/v1/analytics/summary",
            "all_metrics": "/api/v1/analytics/metrics",
            "specific_metric": "/api/v1/analytics/{metric_name}",
            "live_data": "/api/v1/analytics/live"
        }
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "sqlite",
        "environment": "development",
        "database_file": DB_PATH,
        "database_exists": os.path.exists(DB_PATH)
    })

@app.route('/api/v1/analytics/summary')
def get_analytics_summary():
    """Get analytics summary data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get latest data for each metric
        cursor.execute("""
            SELECT metric_name, value, timestamp
            FROM analytics_data
            WHERE (metric_name, timestamp) IN (
                SELECT metric_name, MAX(timestamp)
                FROM analytics_data
                GROUP BY metric_name
            )
            ORDER BY metric_name
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        summary = {}
        for metric_name, value, timestamp in results:
            summary[metric_name] = {
                "value": value,
                "timestamp": timestamp,
                "formatted_value": format_metric_value(metric_name, value)
            }
        
        return jsonify({
            "status": "success",
            "data": summary,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/analytics/metrics')
def get_all_metrics():
    """Get all metrics data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT metric_name, value, timestamp, created_at
            FROM analytics_data
            ORDER BY timestamp DESC, metric_name
            LIMIT 100
        """)
        
        results = cursor.fetchall()
        conn.close()
        
        metrics = []
        for metric_name, value, timestamp, created_at in results:
            metrics.append({
                "metric_name": metric_name,
                "value": value,
                "timestamp": timestamp,
                "created_at": created_at,
                "formatted_value": format_metric_value(metric_name, value)
            })
        
        return jsonify({
            "status": "success",
            "data": metrics,
            "count": len(metrics),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/analytics/<metric_name>')
def get_metric_data(metric_name):
    """Get data for a specific metric"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT value, timestamp, created_at
            FROM analytics_data
            WHERE metric_name = ?
            ORDER BY timestamp DESC
            LIMIT 50
        """, (metric_name,))
        
        results = cursor.fetchall()
        conn.close()
        
        data = []
        for value, timestamp, created_at in results:
            data.append({
                "value": value,
                "timestamp": timestamp,
                "created_at": created_at,
                "formatted_value": format_metric_value(metric_name, value)
            })
        
        return jsonify({
            "status": "success",
            "metric_name": metric_name,
            "data": data,
            "count": len(data),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/api/v1/analytics/live')
def get_live_data():
    """Generate some live/simulated data for demonstration"""
    try:
        # Simulate real-time data by adding some randomness to base values
        base_values = {
            "revenue": 16000,
            "users": 350,
            "orders": 30,
            "conversion_rate": 8.5,
            "page_views": 1300,
            "bounce_rate": 44.0
        }
        
        live_data = {}
        current_time = datetime.now().isoformat()
        
        for metric, base_value in base_values.items():
            # Add some random variation
            if metric == "revenue":
                variation = random.uniform(-1000, 2000)
            elif metric == "users":
                variation = random.randint(-20, 50)
            elif metric == "orders":
                variation = random.randint(-5, 10)
            elif metric == "conversion_rate":
                variation = random.uniform(-1.0, 2.0)
            elif metric == "page_views":
                variation = random.randint(-100, 200)
            elif metric == "bounce_rate":
                variation = random.uniform(-5.0, 5.0)
            else:
                variation = 0
            
            new_value = max(0, base_value + variation)  # Ensure non-negative values
            
            live_data[metric] = {
                "value": round(new_value, 2),
                "timestamp": current_time,
                "formatted_value": format_metric_value(metric, new_value),
                "change": round(variation, 2),
                "change_percent": round((variation / base_value) * 100, 2) if base_value != 0 else 0
            }
        
        return jsonify({
            "status": "success",
            "data": live_data,
            "timestamp": current_time,
            "note": "This is simulated live data for demonstration"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def format_metric_value(metric_name, value):
    """Format metric values for display"""
    if metric_name == "revenue":
        return f"${value:,.2f}"
    elif metric_name in ["users", "orders", "page_views"]:
        return f"{int(value):,}"
    elif metric_name in ["conversion_rate", "bounce_rate"]:
        return f"{value:.1f}%"
    else:
        return str(value)

if __name__ == '__main__':
    # Initialize database
    init_db()
    print("Analytics Dashboard API starting...")
    print("Database initialized with sample data")
    print("\nAPI Endpoints:")
    print("- Root: http://localhost:8000/")
    print("- Health: http://localhost:8000/health")
    print("- Summary: http://localhost:8000/api/v1/analytics/summary")
    print("- All Metrics: http://localhost:8000/api/v1/analytics/metrics")
    print("- Live Data: http://localhost:8000/api/v1/analytics/live")
    print("\nStarting Flask server...")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=8000, debug=True)
