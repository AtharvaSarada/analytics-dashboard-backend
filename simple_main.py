"""
Simple FastAPI Application for Quick Start
A minimal version of the analytics dashboard API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import sqlite3
import os

# Create simple FastAPI app
app = FastAPI(
    title="Real-time Analytics Dashboard API",
    version="1.0.0",
    description="A simple analytics dashboard API"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("analytics.db")
    cursor = conn.cursor()
    
    # Create a simple analytics table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert some sample data
    sample_data = [
        ("revenue", 15420.50, "2024-01-15T10:00:00"),
        ("users", 342, "2024-01-15T10:00:00"),
        ("orders", 28, "2024-01-15T10:00:00"),
        ("conversion_rate", 8.2, "2024-01-15T10:00:00"),
        ("revenue", 16200.25, "2024-01-15T11:00:00"),
        ("users", 367, "2024-01-15T11:00:00"),
        ("orders", 31, "2024-01-15T11:00:00"),
        ("conversion_rate", 8.4, "2024-01-15T11:00:00"),
    ]
    
    cursor.executemany(
        "INSERT OR REPLACE INTO analytics_data (metric_name, value, timestamp) VALUES (?, ?, ?)",
        sample_data
    )
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Real-time Analytics Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "docs": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "sqlite",
        "environment": "development"
    }

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary data"""
    conn = sqlite3.connect("analytics.db")
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
            "timestamp": timestamp
        }
    
    return {
        "status": "success",
        "data": summary,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/analytics/metrics")
async def get_all_metrics():
    """Get all metrics data"""
    conn = sqlite3.connect("analytics.db")
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
            "created_at": created_at
        })
    
    return {
        "status": "success",
        "data": metrics,
        "count": len(metrics),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/analytics/{metric_name}")
async def get_metric_data(metric_name: str):
    """Get data for a specific metric"""
    conn = sqlite3.connect("analytics.db")
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
            "created_at": created_at
        })
    
    return {
        "status": "success",
        "metric_name": metric_name,
        "data": data,
        "count": len(data),
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
