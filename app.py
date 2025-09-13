"""
Real-Time Analytics Dashboard Backend
Flask application with WebSocket support, authentication, and comprehensive API
"""

from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit, disconnect, join_room, leave_room
from flask_cors import CORS
import sqlite3
import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
import threading
import time
import random
import os
from functools import wraps
import json

# Configuration
SECRET_KEY = os.getenv('SECRET_KEY', 'your-super-secret-key-change-in-production')
DB_PATH = "analytics.db"
REFRESH_INTERVAL = 5  # seconds

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:5173", "http://localhost:3000"])
CORS(app, origins=["http://localhost:3000", "http://localhost:5173"])

# Global variables for real-time data
connected_clients = set()
real_time_data = {}
data_generation_thread = None

def init_database():
    """Initialize SQLite database with comprehensive schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table for authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # Analytics data table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analytics_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp TEXT NOT NULL,
            category TEXT DEFAULT 'general',
            source TEXT DEFAULT 'system',
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Dashboards table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            config TEXT,
            is_public BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    # Create default admin user if not exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'admin'")
    if cursor.fetchone()[0] == 0:
        admin_password = bcrypt.hashpw('admin123'.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, role) 
            VALUES (?, ?, ?, ?)
        """, ('admin', 'admin@analytics.com', admin_password.decode('utf-8'), 'admin'))
    
    # Insert comprehensive sample data
    cursor.execute("SELECT COUNT(*) FROM analytics_data")
    if cursor.fetchone()[0] == 0:
        sample_data = generate_comprehensive_sample_data()
        cursor.executemany("""
            INSERT INTO analytics_data (metric_name, value, timestamp, category, source) 
            VALUES (?, ?, ?, ?, ?)
        """, sample_data)
        print("Comprehensive sample data inserted")
    
    conn.commit()
    conn.close()

def generate_comprehensive_sample_data():
    """Generate comprehensive sample data for analytics"""
    data = []
    base_time = datetime.now() - timedelta(days=7)
    
    # Different categories and metrics
    metrics = {
        'sales': ['revenue', 'orders', 'average_order_value', 'refunds'],
        'users': ['active_users', 'new_signups', 'user_retention', 'churn_rate'],
        'performance': ['page_load_time', 'bounce_rate', 'session_duration', 'error_rate'],
        'marketing': ['conversion_rate', 'click_through_rate', 'cost_per_acquisition', 'roi'],
        'geography': ['us_visitors', 'eu_visitors', 'asia_visitors', 'other_visitors']
    }
    
    # Generate data for the past week with hourly intervals
    for day in range(7):
        for hour in range(24):
            current_time = (base_time + timedelta(days=day, hours=hour)).isoformat()
            
            for category, metric_list in metrics.items():
                for metric in metric_list:
                    value = generate_realistic_value(metric, day, hour)
                    data.append((metric, value, current_time, category, 'historical'))
    
    return data

def generate_realistic_value(metric, day, hour):
    """Generate realistic values based on metric type and time patterns"""
    base_values = {
        'revenue': 1000 + (day * 100) + (hour * 50) + random.uniform(-200, 300),
        'orders': 15 + (day * 2) + random.randint(-3, 8),
        'average_order_value': 65 + random.uniform(-10, 20),
        'refunds': random.randint(0, 5),
        'active_users': 200 + (day * 10) + (hour * 5) + random.randint(-20, 40),
        'new_signups': 5 + random.randint(0, 15),
        'user_retention': 75 + random.uniform(-5, 10),
        'churn_rate': 5 + random.uniform(-2, 3),
        'page_load_time': 1.2 + random.uniform(-0.3, 0.8),
        'bounce_rate': 45 + random.uniform(-10, 15),
        'session_duration': 180 + random.randint(-60, 120),
        'error_rate': random.uniform(0, 2),
        'conversion_rate': 8 + random.uniform(-2, 4),
        'click_through_rate': 3.5 + random.uniform(-1, 2),
        'cost_per_acquisition': 25 + random.uniform(-5, 15),
        'roi': 150 + random.uniform(-30, 50),
        'us_visitors': 40 + random.randint(-5, 15),
        'eu_visitors': 30 + random.randint(-5, 10),
        'asia_visitors': 20 + random.randint(-3, 8),
        'other_visitors': 10 + random.randint(-2, 5)
    }
    
    return max(0, base_values.get(metric, random.uniform(1, 100)))

def create_token(user_data):
    """Create JWT token for authentication"""
    payload = {
        'user_id': user_data['id'],
        'username': user_data['username'],
        'role': user_data['role'],
        'exp': datetime.now(timezone.utc) + timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user = payload
        return f(*args, **kwargs)
    
    return decorated_function

# Real-time data generation thread
def generate_real_time_data():
    """Generate real-time data and emit via WebSocket"""
    global real_time_data
    
    while True:
        if connected_clients:
            # Generate new values for key metrics
            metrics = ['revenue', 'active_users', 'orders', 'conversion_rate', 'page_views']
            new_data = {}
            
            for metric in metrics:
                base_value = get_latest_metric_value(metric)
                variation = generate_realistic_variation(metric)
                new_value = max(0, base_value + variation)
                
                new_data[metric] = {
                    'value': round(new_value, 2),
                    'timestamp': datetime.now().isoformat(),
                    'change': round(variation, 2),
                    'change_percent': round((variation / base_value) * 100, 2) if base_value != 0 else 0
                }
            
            real_time_data = new_data
            socketio.emit('analytics_update', new_data, room='analytics')
            
            # Store in database
            store_real_time_data(new_data)
        
        time.sleep(REFRESH_INTERVAL)

def get_latest_metric_value(metric):
    """Get the latest value for a metric"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT value FROM analytics_data 
        WHERE metric_name = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    """, (metric,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else generate_realistic_value(metric, 0, 12)

def generate_realistic_variation(metric):
    """Generate realistic variations for real-time updates"""
    variations = {
        'revenue': random.uniform(-100, 200),
        'active_users': random.randint(-10, 25),
        'orders': random.randint(-2, 5),
        'conversion_rate': random.uniform(-0.5, 1.0),
        'page_views': random.randint(-50, 100)
    }
    return variations.get(metric, random.uniform(-5, 10))

def store_real_time_data(data):
    """Store real-time data in database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for metric, info in data.items():
        cursor.execute("""
            INSERT INTO analytics_data (metric_name, value, timestamp, category, source) 
            VALUES (?, ?, ?, ?, ?)
        """, (metric, info['value'], info['timestamp'], 'realtime', 'live'))
    
    conn.commit()
    conn.close()

# API Routes

@app.route('/')
def root():
    """Root endpoint with comprehensive API documentation"""
    return jsonify({
        "message": "Real-Time Analytics Dashboard API",
        "version": "2.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "features": [
            "Real-time WebSocket updates",
            "JWT Authentication",
            "Comprehensive analytics data",
            "Dashboard management",
            "Multi-category metrics"
        ],
        "endpoints": {
            "authentication": {
                "login": "POST /api/v1/auth/login",
                "register": "POST /api/v1/auth/register",
                "profile": "GET /api/v1/auth/profile"
            },
            "analytics": {
                "summary": "GET /api/v1/analytics/summary",
                "metrics": "GET /api/v1/analytics/metrics",
                "category": "GET /api/v1/analytics/category/{category}",
                "realtime": "GET /api/v1/analytics/realtime",
                "historical": "GET /api/v1/analytics/historical"
            },
            "dashboards": {
                "list": "GET /api/v1/dashboards",
                "create": "POST /api/v1/dashboards",
                "get": "GET /api/v1/dashboards/{id}",
                "update": "PUT /api/v1/dashboards/{id}",
                "delete": "DELETE /api/v1/dashboards/{id}"
            },
            "websocket": "Connect to / for real-time updates"
        }
    })

@app.route('/health')
def health():
    """Enhanced health check"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM analytics_data")
    data_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": "sqlite",
        "data_points": data_count,
        "users": user_count,
        "websocket_clients": len(connected_clients),
        "real_time_active": data_generation_thread and data_generation_thread.is_alive()
    })

# Authentication Routes
@app.route('/api/v1/auth/register', methods=['POST'])
def register():
    """User registration"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': 'Username, email, and password required'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", 
                   (data['username'], data['email']))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Username or email already exists'}), 400
    
    # Create user
    password_hash = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
    cursor.execute("""
        INSERT INTO users (username, email, password_hash) 
        VALUES (?, ?, ?)
    """, (data['username'], data['email'], password_hash.decode('utf-8')))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Create token
    user_data = {
        'id': user_id,
        'username': data['username'],
        'role': 'user'
    }
    token = create_token(user_data)
    
    return jsonify({
        'message': 'User registered successfully',
        'token': token,
        'user': user_data
    }), 201

@app.route('/api/v1/auth/login', methods=['POST'])
def login():
    """User login"""
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, username, email, password_hash, role 
        FROM users WHERE username = ? OR email = ?
    """, (data['username'], data['username']))
    
    user = cursor.fetchone()
    conn.close()
    
    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user[3].encode('utf-8')):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Update last login
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_login = ? WHERE id = ?", 
                   (datetime.now().isoformat(), user[0]))
    conn.commit()
    conn.close()
    
    user_data = {
        'id': user[0],
        'username': user[1],
        'email': user[2],
        'role': user[4]
    }
    
    token = create_token(user_data)
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user_data
    })

@app.route('/api/v1/auth/profile')
@require_auth
def profile():
    """Get user profile"""
    return jsonify({
        'user': request.user,
        'timestamp': datetime.now().isoformat()
    })

# Analytics Routes
@app.route('/api/v1/analytics/summary')
def analytics_summary():
    """Get comprehensive analytics summary"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get latest data for key metrics by category
    cursor.execute("""
        SELECT category, metric_name, value, timestamp
        FROM analytics_data
        WHERE (metric_name, timestamp) IN (
            SELECT metric_name, MAX(timestamp)
            FROM analytics_data
            GROUP BY metric_name
        )
        ORDER BY category, metric_name
    """)
    
    results = cursor.fetchall()
    conn.close()
    
    summary = {}
    for category, metric_name, value, timestamp in results:
        if category not in summary:
            summary[category] = {}
        
        summary[category][metric_name] = {
            'value': value,
            'timestamp': timestamp,
            'formatted': format_metric_value(metric_name, value)
        }
    
    return jsonify({
        'status': 'success',
        'data': summary,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/analytics/category/<category>')
def analytics_by_category(category):
    """Get analytics data by category"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT metric_name, value, timestamp, source
        FROM analytics_data
        WHERE category = ?
        ORDER BY timestamp DESC, metric_name
        LIMIT 200
    """, (category,))
    
    results = cursor.fetchall()
    conn.close()
    
    metrics = []
    for metric_name, value, timestamp, source in results:
        metrics.append({
            'metric_name': metric_name,
            'value': value,
            'timestamp': timestamp,
            'source': source,
            'formatted': format_metric_value(metric_name, value)
        })
    
    return jsonify({
        'status': 'success',
        'category': category,
        'data': metrics,
        'count': len(metrics)
    })

@app.route('/api/v1/analytics/realtime')
def realtime_data():
    """Get current real-time data"""
    return jsonify({
        'status': 'success',
        'data': real_time_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/v1/analytics/historical')
def historical_data():
    """Get historical data with aggregation options"""
    timeframe = request.args.get('timeframe', '24h')
    metric = request.args.get('metric', None)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Calculate time range
    if timeframe == '1h':
        start_time = datetime.now() - timedelta(hours=1)
    elif timeframe == '24h':
        start_time = datetime.now() - timedelta(hours=24)
    elif timeframe == '7d':
        start_time = datetime.now() - timedelta(days=7)
    elif timeframe == '30d':
        start_time = datetime.now() - timedelta(days=30)
    else:
        start_time = datetime.now() - timedelta(hours=24)
    
    query = """
        SELECT metric_name, value, timestamp, category
        FROM analytics_data
        WHERE timestamp >= ?
    """
    params = [start_time.isoformat()]
    
    if metric:
        query += " AND metric_name = ?"
        params.append(metric)
    
    query += " ORDER BY timestamp DESC LIMIT 1000"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    data = []
    for metric_name, value, timestamp, category in results:
        data.append({
            'metric_name': metric_name,
            'value': value,
            'timestamp': timestamp,
            'category': category,
            'formatted': format_metric_value(metric_name, value)
        })
    
    return jsonify({
        'status': 'success',
        'timeframe': timeframe,
        'metric': metric,
        'data': data,
        'count': len(data)
    })

# Dashboard Routes
@app.route('/api/v1/dashboards')
@require_auth
def get_dashboards():
    """Get user dashboards"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if request.user['role'] == 'admin':
        cursor.execute("""
            SELECT d.id, d.name, d.description, d.is_public, d.created_at,
                   u.username as owner
            FROM dashboards d
            LEFT JOIN users u ON d.user_id = u.id
            ORDER BY d.created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT id, name, description, is_public, created_at
            FROM dashboards
            WHERE user_id = ? OR is_public = 1
            ORDER BY created_at DESC
        """, (request.user['user_id'],))
    
    dashboards = []
    for row in cursor.fetchall():
        if request.user['role'] == 'admin':
            dashboard = {
                'id': row[0], 'name': row[1], 'description': row[2],
                'is_public': row[3], 'created_at': row[4], 'owner': row[5]
            }
        else:
            dashboard = {
                'id': row[0], 'name': row[1], 'description': row[2],
                'is_public': row[3], 'created_at': row[4]
            }
        dashboards.append(dashboard)
    
    conn.close()
    
    return jsonify({
        'status': 'success',
        'data': dashboards,
        'count': len(dashboards)
    })

def format_metric_value(metric_name, value):
    """Enhanced metric formatting"""
    formatters = {
        'revenue': lambda x: f"${x:,.2f}",
        'orders': lambda x: f"{int(x):,}",
        'active_users': lambda x: f"{int(x):,}",
        'new_signups': lambda x: f"{int(x):,}",
        'page_views': lambda x: f"{int(x):,}",
        'conversion_rate': lambda x: f"{x:.1f}%",
        'bounce_rate': lambda x: f"{x:.1f}%",
        'user_retention': lambda x: f"{x:.1f}%",
        'churn_rate': lambda x: f"{x:.1f}%",
        'click_through_rate': lambda x: f"{x:.1f}%",
        'error_rate': lambda x: f"{x:.2f}%",
        'roi': lambda x: f"{x:.0f}%",
        'page_load_time': lambda x: f"{x:.2f}s",
        'session_duration': lambda x: f"{int(x//60)}m {int(x%60)}s",
        'average_order_value': lambda x: f"${x:.2f}",
        'cost_per_acquisition': lambda x: f"${x:.2f}",
        'refunds': lambda x: f"{int(x)}",
        'us_visitors': lambda x: f"{int(x)}%",
        'eu_visitors': lambda x: f"{int(x)}%",
        'asia_visitors': lambda x: f"{int(x)}%",
        'other_visitors': lambda x: f"{int(x)}%"
    }
    
    formatter = formatters.get(metric_name, lambda x: str(x))
    return formatter(value)

# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    connected_clients.add(request.sid)
    join_room('analytics')
    emit('connection_status', {'status': 'connected', 'timestamp': datetime.now().isoformat()})
    
    # Send current real-time data
    if real_time_data:
        emit('analytics_update', real_time_data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    connected_clients.discard(request.sid)
    leave_room('analytics')

@socketio.on('subscribe_to_metric')
def handle_metric_subscription(data):
    """Handle subscription to specific metrics"""
    metric_name = data.get('metric')
    if metric_name:
        join_room(f'metric_{metric_name}')
        emit('subscription_status', {
            'metric': metric_name,
            'status': 'subscribed',
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start real-time data generation thread
    data_generation_thread = threading.Thread(target=generate_real_time_data, daemon=True)
    data_generation_thread.start()
    
    print("🚀 Real-Time Analytics Dashboard API v2.0")
    print("✅ Database initialized with comprehensive data")
    print("✅ WebSocket support enabled")
    print("✅ JWT Authentication enabled")
    print("✅ Real-time data generation started")
    print(f"✅ Default admin login: username='admin', password='admin123'")
    print("\n📊 Enhanced API Features:")
    print("- Multi-category analytics")
    print("- Real-time WebSocket updates")
    print("- User authentication & dashboards")
    print("- Historical data with aggregation")
    print("- Comprehensive sample dataset")
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=8000, debug=True)
