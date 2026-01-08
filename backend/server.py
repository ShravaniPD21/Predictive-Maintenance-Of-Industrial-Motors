# """
# Flask Backend Server for Motor Monitoring Dashboard
# Real-time data streaming with WebSocket support
# Author: IoT Motor Monitoring Project
# """

# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from flask_socketio import SocketIO, emit
# import joblib
# import pandas as pd
# import numpy as np
# from datetime import datetime, timedelta
# import json
# import threading
# import time
# import serial

# app = Flask(__name__)
# CORS(app)
# socketio = SocketIO(app, cors_allowed_origins="*")

# # ============================================================================
# # GLOBAL VARIABLES AND CONFIGURATION
# # ============================================================================

# # Load trained model
# model = joblib.load('motor_failure_model.pkl')
# scaler = joblib.load('feature_scaler.pkl')
# feature_cols = joblib.load('feature_columns.pkl')

# # Store latest data
# latest_data = {
#     'timestamp': datetime.now().isoformat(),
#     'temperature': 75.5,
#     'vibration': 2.3,
#     'current': 12.5,
#     'speed': 1450,
#     'torque': 42.0,
#     'tool_wear': 120,
#     'status': 'NORMAL',
#     'prediction_confidence': 0.95,
#     'alerts': []
# }

# # Historical data storage (last 100 readings)
# historical_data = []
# max_history = 100

# # Alert thresholds
# THRESHOLDS = {
#     'temperature': {'warning': 85, 'critical': 95},
#     'vibration': {'warning': 3.0, 'critical': 4.5},
#     'current': {'warning': 15, 'critical': 18},
#     'speed_low': {'warning': 1200, 'critical': 1000},
#     'torque': {'warning': 50, 'critical': 60},
#     'tool_wear': {'warning': 180, 'critical': 220}
# }

# # STM32 Serial connection (optional)
# stm32_serial = None
# USE_REAL_DATA = False  # Set to True when STM32 is connected


# # ============================================================================
# # SERIAL COMMUNICATION WITH STM32
# # ============================================================================

# def init_serial_connection(port='COM3', baudrate=9600):
#     """Initialize serial connection to STM32"""
#     global stm32_serial, USE_REAL_DATA
#     try:
#         stm32_serial = serial.Serial(port, baudrate, timeout=1)
#         USE_REAL_DATA = True
#         print(f"✓ Connected to STM32 on {port}")
#         return True
#     except Exception as e:
#         print(f"⚠️ STM32 not connected: {e}")
#         print("Using simulated data...")
#         USE_REAL_DATA = False
#         return False


# def read_stm32_data():
#     """Read data from STM32 via serial"""
#     global stm32_serial
    
#     if stm32_serial and stm32_serial.is_open:
#         try:
#             line = stm32_serial.readline().decode('utf-8').strip()
#             if line:
#                 data = json.loads(line)
#                 return data
#         except Exception as e:
#             print(f"Error reading STM32 data: {e}")
    
#     return None


# # ============================================================================
# # DATA PROCESSING AND PREDICTION
# # ============================================================================

# def process_sensor_data(raw_data):
#     """Process sensor data and make prediction"""
    
#     # Convert raw data to model format
#     model_input = {
#         'Air temperature [K]': raw_data.get('air_temp_k', 298.0),
#         'Process temperature [K]': raw_data.get('process_temp_k', 308.0),
#         'Rotational speed [rpm]': raw_data.get('speed', 1450),
#         'Torque [Nm]': raw_data.get('torque', 40.0),
#         'Tool wear [min]': raw_data.get('tool_wear', 120),
#         'Type_Encoded': raw_data.get('type', 1)
#     }
    
#     # Engineer features
#     df = pd.DataFrame([model_input])
    
#     # Temperature features
#     df['Temp_Difference'] = df['Process temperature [K]'] - df['Air temperature [K]']
#     df['Temp_Ratio'] = df['Process temperature [K]'] / df['Air temperature [K]']
#     df['Process_Temp_C'] = df['Process temperature [K]'] - 273.15
#     df['Air_Temp_C'] = df['Air temperature [K]'] - 273.15
#     df['High_Process_Temp'] = (df['Process_Temp_C'] > 85).astype(int)
#     df['High_Temp_Diff'] = (df['Temp_Difference'] > 10).astype(int)
    
#     # Power features
#     df['Power'] = df['Torque [Nm]'] * df['Rotational speed [rpm]'] * 2 * np.pi / 60
#     df['Torque_Speed_Ratio'] = df['Torque [Nm]'] / (df['Rotational speed [rpm]'] + 1)
#     df['High_Torque'] = (df['Torque [Nm]'] > 50).astype(int)
#     df['Low_Speed'] = (df['Rotational speed [rpm]'] < 1200).astype(int)
    
#     # Tool wear features
#     df['High_Tool_Wear'] = (df['Tool wear [min]'] > 200).astype(int)
    
#     # Risk score
#     df['Risk_Score'] = (df['High_Process_Temp'] + df['High_Temp_Diff'] + 
#                         df['High_Torque'] + df['Low_Speed'] + df['High_Tool_Wear'])
    
#     # Make prediction
#     try:
#         X = df[feature_cols].values
#         X_scaled = scaler.transform(X)
        
#         prediction = model.predict(X_scaled)[0]
#         probability = model.predict_proba(X_scaled)[0]
        
#         status = 'FAILURE_LIKELY' if prediction == 1 else 'NORMAL'
#         confidence = probability[1] if prediction == 1 else probability[0]
        
#     except Exception as e:
#         print(f"Prediction error: {e}")
#         status = 'ERROR'
#         confidence = 0
    
#     # Check alerts
#     alerts = check_thresholds(df.iloc[0])
    
#     # Format response
#     processed_data = {
#         'timestamp': datetime.now().isoformat(),
#         'temperature': float(df['Process_Temp_C'].values[0]),
#         'vibration': raw_data.get('vibration', 2.3),
#         'current': raw_data.get('current', 12.5),
#         'speed': float(df['Rotational speed [rpm]'].values[0]),
#         'torque': float(df['Torque [Nm]'].values[0]),
#         'tool_wear': int(df['Tool wear [min]'].values[0]),
#         'status': status,
#         'prediction_confidence': float(confidence),
#         'alerts': alerts,
#         'power': float(df['Power'].values[0]),
#         'temp_difference': float(df['Temp_Difference'].values[0])
#     }
    
#     return processed_data


# def check_thresholds(data_row):
#     """Check if any thresholds are exceeded"""
#     alerts = []
    
#     # Temperature
#     temp = data_row['Process_Temp_C']
#     if temp > THRESHOLDS['temperature']['critical']:
#         alerts.append({
#             'level': 'CRITICAL',
#             'type': 'TEMPERATURE',
#             'message': f'Temperature critically high: {temp:.1f}°C',
#             'value': float(temp)
#         })
#     elif temp > THRESHOLDS['temperature']['warning']:
#         alerts.append({
#             'level': 'WARNING',
#             'type': 'TEMPERATURE',
#             'message': f'Temperature elevated: {temp:.1f}°C',
#             'value': float(temp)
#         })
    
#     # Torque
#     torque = data_row['Torque [Nm]']
#     if torque > THRESHOLDS['torque']['critical']:
#         alerts.append({
#             'level': 'CRITICAL',
#             'type': 'TORQUE',
#             'message': f'Torque critically high: {torque:.1f}Nm',
#             'value': float(torque)
#         })
#     elif torque > THRESHOLDS['torque']['warning']:
#         alerts.append({
#             'level': 'WARNING',
#             'type': 'TORQUE',
#             'message': f'Torque elevated: {torque:.1f}Nm',
#             'value': float(torque)
#         })
    
#     # Speed
#     speed = data_row['Rotational speed [rpm]']
#     if speed < THRESHOLDS['speed_low']['critical']:
#         alerts.append({
#             'level': 'CRITICAL',
#             'type': 'SPEED',
#             'message': f'Speed critically low: {speed:.0f}RPM',
#             'value': float(speed)
#         })
#     elif speed < THRESHOLDS['speed_low']['warning']:
#         alerts.append({
#             'level': 'WARNING',
#             'type': 'SPEED',
#             'message': f'Speed low: {speed:.0f}RPM',
#             'value': float(speed)
#         })
    
#     # Tool wear
#     tool_wear = data_row['Tool wear [min]']
#     if tool_wear > THRESHOLDS['tool_wear']['critical']:
#         alerts.append({
#             'level': 'CRITICAL',
#             'type': 'TOOL_WEAR',
#             'message': f'Tool wear critical: {tool_wear}min',
#             'value': int(tool_wear)
#         })
#     elif tool_wear > THRESHOLDS['tool_wear']['warning']:
#         alerts.append({
#             'level': 'WARNING',
#             'type': 'TOOL_WEAR',
#             'message': f'Tool wear high: {tool_wear}min',
#             'value': int(tool_wear)
#         })
    
#     return alerts


# def generate_simulated_data():
#     """Generate simulated sensor data for testing"""
#     base_temp = 75 + np.random.normal(0, 3)
#     base_vibration = 2.3 + np.random.normal(0, 0.2)
#     base_current = 12.5 + np.random.normal(0, 0.5)
#     base_speed = 1450 + np.random.normal(0, 20)
#     base_torque = 42 + np.random.normal(0, 2)
    
#     # Occasionally simulate anomalies
#     if np.random.random() < 0.8:  # 5% chance
#         anomaly_type = np.random.choice(['temp', 'vibration', 'torque'])
#         if anomaly_type == 'temp':
#             base_temp = 92 + np.random.normal(0, 2)
#         elif anomaly_type == 'vibration':
#             base_vibration = 4.5 + np.random.normal(0, 0.3)
#         elif anomaly_type == 'torque':
#             base_torque = 58 + np.random.normal(0, 2)
    
#     return {
#         'process_temp_k': base_temp + 273.15,
#         'air_temp_k': 298.0,
#         'speed': max(0, base_speed),
#         'torque': max(0, base_torque),
#         'tool_wear': np.random.randint(100, 200),
#         'vibration': max(0, base_vibration),
#         'current': max(0, base_current),
#         'type': 1
#     }


# # ============================================================================
# # REST API ENDPOINTS
# # ============================================================================

# @app.route('/api/status', methods=['GET'])
# def get_status():
#     """Get current motor status"""
#     return jsonify(latest_data)


# @app.route('/api/history', methods=['GET'])
# def get_history():
#     """Get historical data"""
#     limit = request.args.get('limit', 100, type=int)
#     return jsonify(historical_data[-limit:])


# @app.route('/api/alerts', methods=['GET'])
# def get_alerts():
#     """Get current alerts"""
#     return jsonify({
#         'alerts': latest_data.get('alerts', []),
#         'alert_count': len(latest_data.get('alerts', []))
#     })


# @app.route('/api/statistics', methods=['GET'])
# def get_statistics():
#     """Get statistical summary"""
#     if len(historical_data) == 0:
#         return jsonify({'error': 'No data available'})
    
#     df = pd.DataFrame(historical_data)
    
#     stats = {
#         'temperature': {
#             'current': float(latest_data['temperature']),
#             'average': float(df['temperature'].mean()),
#             'min': float(df['temperature'].min()),
#             'max': float(df['temperature'].max())
#         },
#         'vibration': {
#             'current': float(latest_data['vibration']),
#             'average': float(df['vibration'].mean()),
#             'min': float(df['vibration'].min()),
#             'max': float(df['vibration'].max())
#         },
#         'current': {
#             'current': float(latest_data['current']),
#             'average': float(df['current'].mean()),
#             'min': float(df['current'].min()),
#             'max': float(df['current'].max())
#         },
#         'uptime_percentage': 99.4,
#         'total_predictions': len(historical_data),
#         'failure_predictions': sum(1 for d in historical_data if d['status'] == 'FAILURE_LIKELY')
#     }
    
#     return jsonify(stats)


# @app.route('/api/thresholds', methods=['GET'])
# def get_thresholds():
#     """Get configured thresholds"""
#     return jsonify(THRESHOLDS)


# @app.route('/api/thresholds', methods=['POST'])
# def update_thresholds():
#     """Update threshold values"""
#     global THRESHOLDS
#     data = request.json
#     THRESHOLDS.update(data)
#     return jsonify({'message': 'Thresholds updated', 'thresholds': THRESHOLDS})


# # ============================================================================
# # WEBSOCKET EVENTS
# # ============================================================================

# @socketio.on('connect')
# def handle_connect():
#     """Handle client connection"""
#     print('Client connected')
#     emit('connection_response', {'status': 'connected'})


# @socketio.on('disconnect')
# def handle_disconnect():
#     """Handle client disconnection"""
#     print('Client disconnected')


# @socketio.on('request_data')
# def handle_data_request():
#     """Handle data request from client"""
#     emit('motor_data', latest_data)


# # ============================================================================
# # BACKGROUND DATA COLLECTION
# # ============================================================================

# def data_collection_loop():
#     """Background thread for continuous data collection"""
#     global latest_data, historical_data
    
#     print("Starting data collection loop...")
    
#     while True:
#         try:
#             # Get data from STM32 or simulate
#             if USE_REAL_DATA:
#                 raw_data = read_stm32_data()
#                 if raw_data is None:
#                     raw_data = generate_simulated_data()
#             else:
#                 raw_data = generate_simulated_data()
            
#             # Process data and make prediction
#             processed_data = process_sensor_data(raw_data)
            
#             # Update latest data
#             latest_data = processed_data
            
#             # Add to history
#             historical_data.append(processed_data)
#             if len(historical_data) > max_history:
#                 historical_data.pop(0)
            
#             # Emit data to all connected clients
#             socketio.emit('motor_data', processed_data)
            
#             # If there are critical alerts, emit alert notification
#             critical_alerts = [a for a in processed_data['alerts'] if a['level'] == 'CRITICAL']
#             if critical_alerts:
#                 socketio.emit('critical_alert', {
#                     'message': 'CRITICAL ALERT DETECTED',
#                     'alerts': critical_alerts,
#                     'timestamp': processed_data['timestamp']
#                 })
            
#             time.sleep(2)  # Update every 2 seconds
            
#         except Exception as e:
#             print(f"Error in data collection loop: {e}")
#             time.sleep(5)


# # ============================================================================
# # MAIN APPLICATION
# # ============================================================================

# if __name__ == '__main__':
#     print("\n" + "="*70)
#     print("MOTOR MONITORING BACKEND SERVER")
#     print("="*70)
    
#     # Try to connect to STM32
#     print("\nAttempting to connect to STM32...")
#     init_serial_connection('COM3', 9600)
    
#     # Start background data collection thread
#     collection_thread = threading.Thread(target=data_collection_loop, daemon=True)
#     collection_thread.start()
    
#     # Initialize with some simulated historical data
#     print("\nGenerating initial historical data...")
#     for i in range(20):
#         raw_data = generate_simulated_data()
#         processed_data = process_sensor_data(raw_data)
#         historical_data.append(processed_data)
    
#     print("\n✓ Backend server ready!")
#     print("\nServer running on: http://localhost:5000")
#     print("API Endpoints:")
#     print("  GET  /api/status       - Current motor status")
#     print("  GET  /api/history      - Historical data")
#     print("  GET  /api/alerts       - Current alerts")
#     print("  GET  /api/statistics   - Statistical summary")
#     print("  GET  /api/thresholds   - Current thresholds")
#     print("  POST /api/thresholds   - Update thresholds")
#     print("\nWebSocket: ws://localhost:5000")
#     print("\nPress Ctrl+C to stop\n")
    
#     # Run Flask-SocketIO server
#     socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)





from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import json
import threading
import time
import serial

# Firebase (optional)
try:
    import firebase_admin
    from firebase_admin import credentials, messaging
    FIREBASE_ENABLED = False
except ImportError:
    print("⚠️ Firebase not installed. Push notifications disabled.")
    FIREBASE_ENABLED = False

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# ----------------------------- GLOBALS -----------------------------
model = joblib.load('motor_failure_model.pkl')
scaler = joblib.load('feature_scaler.pkl')
feature_cols = joblib.load('feature_columns.pkl')

latest_data = {}
historical_data = []
latest_alerts = []
max_history = 100

THRESHOLDS = {
    'temperature': {'warning': 50, 'critical': 70},
    'vibration': {'warning': 5.0, 'critical': 8.0},
    'current': {'warning': 5, 'critical': 8},
    'humidity': {'warning': 60, 'critical': 75},
}

stm32_serial = None
USE_REAL_DATA = True
device_tokens = []
last_alert_time = {}

# ----------------------------- FIREBASE -----------------------------
def init_firebase():
    global FIREBASE_ENABLED
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred)
        FIREBASE_ENABLED = True
        print("✅ Firebase initialized - Push notifications enabled")
    except Exception as e:
        print(f"⚠️ Firebase not configured: {e}")
        FIREBASE_ENABLED = False

# ----------------------------- NOTIFICATIONS -----------------------------
def send_push_notification(title, body, data=None):
    if not FIREBASE_ENABLED or not device_tokens:
        return
    message = messaging.MulticastMessage(
        notification=messaging.Notification(title=title, body=body),
        data=data if data else {},
        tokens=device_tokens,
        android=messaging.AndroidConfig(
            priority='high',
            notification=messaging.AndroidNotification(channel_id='threshold-alerts', sound='default', priority='high')
        )
    )
    try:
        response = messaging.send_multicast(message)
        print(f'📲 Notification sent: {response.success_count} succeeded, {response.failure_count} failed')
    except Exception as e:
        print(f'❌ Error sending notification: {e}')

def check_thresholds_and_notify(processed_data):
    global latest_alerts
    current_time = time.time()
    alerts = []
    for param in ['temperature', 'vibration', 'current', 'humidity']:
        value = processed_data.get(param, 0)
        thresholds = THRESHOLDS.get(param, {})

        # Critical
        if value > thresholds.get('critical', float('inf')):
            alert_key = f"{param}_critical"
            if current_time - last_alert_time.get(alert_key, 0) > 60:
                alert_msg = f"🚨 CRITICAL: {param.upper()} = {value:.2f} (Limit: {thresholds['critical']})"
                alerts.append({'level':'critical','parameter':param,'value':value,'threshold':thresholds['critical'],'message':alert_msg})
                send_push_notification("🚨 Critical Alert!", alert_msg, data={'parameter':param,'value':str(value),'threshold':str(thresholds['critical']),'level':'critical'})
                last_alert_time[alert_key] = current_time
                print(f"🚨 {alert_msg}")

        # Warning
        elif value > thresholds.get('warning', float('inf')):
            alert_key = f"{param}_warning"
            if current_time - last_alert_time.get(alert_key, 0) > 120:
                alert_msg = f"⚠️ WARNING: {param.upper()} = {value:.2f} (Limit: {thresholds['warning']})"
                alerts.append({'level':'warning','parameter':param,'value':value,'threshold':thresholds['warning'],'message':alert_msg})
                send_push_notification("⚠️ Warning Alert", alert_msg, data={'parameter':param,'value':str(value),'threshold':str(thresholds['warning']),'level':'warning'})
                last_alert_time[alert_key] = current_time
                print(f"⚠️ {alert_msg}")

    if alerts:
        socketio.emit('threshold_alert', alerts, broadcast=True)
        latest_alerts = alerts  # store latest alerts for HTTP access

    return alerts

# ----------------------------- SERIAL -----------------------------
def init_serial_connection(port="COM5", baudrate=115200):
    global stm32_serial, USE_REAL_DATA
    try:
        stm32_serial = serial.Serial(port, baudrate, timeout=1)
        USE_REAL_DATA = True
        print(f"✅ Connected to STM32 on {port} @ {baudrate} baud")
        return True
    except Exception as e:
        print(f"⚠️ STM32 not connected: {e}")
        USE_REAL_DATA = False
        return False

def read_stm32_data():
    global stm32_serial
    if stm32_serial and stm32_serial.is_open:
        try:
            line = stm32_serial.readline().decode().strip()
            if line:
                print("📥 Serial →", line)
                return json.loads(line)
        except Exception as e:
            print(f"🚨 Serial JSON Parse Error: {e}")
    return None

# ----------------------------- SENSOR PROCESSING -----------------------------
def process_sensor_data(raw_data):
    model_input = {
        'Air temperature [K]': raw_data.get('air_temp_k', 298.0),
        'Process temperature [K]': raw_data.get('process_temp_k', 308.0),
        'Type_Encoded': raw_data.get('type', 1)
    }
    df = pd.DataFrame([model_input])
    df['Process_Temp_C'] = df['Process temperature [K]'] - 273.15
    X = scaler.transform(df[feature_cols])
    prediction = model.predict(X)[0]
    confidence = model.predict_proba(X)[0][prediction]

    processed = {
        'timestamp': datetime.now().isoformat(),
        'temperature': float(df['Process_Temp_C'].values[0]),
        'vibration': raw_data.get('vibration', 2.3),
        'current': raw_data.get('current', 12.5),
        'humidity': raw_data.get('humidity', 70),
        'status': "FAILURE_LIKELY" if prediction==1 else "NORMAL",
        'prediction_confidence': float(confidence),
        'alerts': []
    }
    alerts = check_thresholds_and_notify(processed)
    processed['alerts'] = alerts
    return processed

# ----------------------------- DATA LOOP -----------------------------
def data_collection_loop():
    global latest_data, historical_data
    print("📡 Data collection thread started")
    while True:
        try:
            raw_data = read_stm32_data() if USE_REAL_DATA else None
            if raw_data is None:
                raw_data = {"process_temp_k":350.0,"air_temp_k":300.0,"humidity":70,"vibration":2.5,"current":10,"type":1}

            processed = process_sensor_data(raw_data)
            latest_data = processed
            historical_data.append(processed)
            if len(historical_data) > max_history:
                historical_data.pop(0)
            socketio.emit("motor_data", processed)
            time.sleep(2)
        except Exception as e:
            print(f"⚠ data loop error: {e}")
            time.sleep(3)

# ----------------------------- API ENDPOINTS -----------------------------
@app.route('/api/register-device', methods=['POST'])
def register_device():
    data = request.json
    token = data.get('device_token')
    platform = data.get('platform','unknown')
    if token and token not in device_tokens:
        device_tokens.append(token)
        print(f"📱 Registered {platform} device: {token[:30]}...")
        return jsonify({'status':'success','message':'Device registered'}),200
    elif token in device_tokens:
        return jsonify({'status':'success','message':'Device already registered'}),200
    return jsonify({'status':'error','message':'Invalid token'}),400

@app.route('/api/unregister-device', methods=['POST'])
def unregister_device():
    data = request.json
    token = data.get('device_token')
    if token in device_tokens:
        device_tokens.remove(token)
        print(f"📱 Unregistered device: {token[:30]}...")
        return jsonify({'status':'success','message':'Device unregistered'}),200
    return jsonify({'status':'error','message':'Token not found'}),404

@app.route('/api/current-data', methods=['GET'])
def get_current_data():
    return jsonify(latest_data),200

@app.route('/api/historical-data', methods=['GET'])
def get_historical_data():
    return jsonify(historical_data),200

@app.route('/api/thresholds', methods=['GET','POST'])
def thresholds():
    if request.method=='GET':
        return jsonify(THRESHOLDS),200
    data = request.json
    for param, values in data.items():
        if param in THRESHOLDS:
            THRESHOLDS[param].update(values)
    print(f"✅ Thresholds updated: {THRESHOLDS}")
    return jsonify({'status':'success','thresholds':THRESHOLDS}),200

@app.route('/api/test-notification', methods=['POST'])
def test_notification():
    send_push_notification("🔔 Test Notification","Your motor monitoring system is working correctly!", data={'type':'test','timestamp':datetime.now().isoformat()})
    socketio.emit('threshold_alert',[{'level':'info','parameter':'system','message':'Test notification sent'}],broadcast=True)
    return jsonify({'status':'success','message':'Test notification sent','devices':len(device_tokens)}),200

# ----------------------------- NEW HTTP ENDPOINTS -----------------------------
@app.route('/api/motor_data', methods=['GET'])
def http_motor_data():
    """Return latest motor data (same as WebSocket)"""
    return jsonify(latest_data),200

@app.route('/api/threshold_alerts', methods=['GET'])
def http_threshold_alerts():
    """Return latest alerts"""
    return jsonify(latest_alerts),200

# ----------------------------- WEBSOCKET -----------------------------
@socketio.on('connect')
def handle_connect():
    print('✅ Client connected to WebSocket')
    if latest_data:
        emit('motor_data', latest_data)
    if latest_alerts:
        emit('threshold_alert', latest_alerts)

@socketio.on('disconnect')
def handle_disconnect():
    print('❌ Client disconnected from WebSocket')

# ----------------------------- MAIN -----------------------------
if __name__ == "__main__":
    print("===========================================")
    print(" MOTOR BACKEND STARTING...")
    print("===========================================")
    init_firebase()
    init_serial_connection("COM5",115200)
    threading.Thread(target=data_collection_loop, daemon=True).start()
    print("✅ Backend Server Ready → http://localhost:5000")
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
