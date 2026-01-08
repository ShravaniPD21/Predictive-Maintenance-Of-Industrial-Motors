import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Activity, AlertTriangle, CheckCircle, Thermometer, Zap, Gauge, Settings, Bell } from 'lucide-react';
import './MotorMonitoringDashboard.css';
import api from "../services/api";


const MotorMonitoringDashboard = () => {
  const [motorData, setMotorData] = useState({
    timestamp: new Date().toISOString(),
    temperature: 75.5,
    vibration: 2.3,
    current: 12.5,
    speed: 1450,
    torque: 42.0,
    tool_wear: 120,
    status: 'NORMAL',
    prediction_confidence: 0.95,
    alerts: []
  });

  const [historicalData, setHistoricalData] = useState([]);
//   const [statistics, setStatistics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

 useEffect(() => {
  // Socket connection debug handlers
  api.socket.on('connect', () => {
    console.log('✅ Connected to backend WebSocket/Socket.IO (transport:', api.socket.io?.transport?.name || 'unknown', ')');
    setIsConnected(true);
  });

  api.socket.on('disconnect', (reason) => {
    console.warn('⚠️ Socket disconnected:', reason);
    setIsConnected(false);
  });

  api.socket.on('connect_error', (err) => {
    console.error('🔌 Socket connect_error:', err);
  });

  // Listen for real-time motor data
  api.socket.on('motor_data', (data) => {
    console.log('📡 Received motor_data:', data);
    setMotorData(data);

    setHistoricalData(prev => {
      const updated = [...prev, {
        time: new Date(data.timestamp).toLocaleTimeString(),
        temperature: data.temperature,
        vibration: data.vibration,
        current: data.current,
        speed: data.speed
      }];
      return updated.slice(-20);
    });

    // Always refresh latest alerts from the backend API (single source of truth).
    api.getAlerts().then((response) => {
      const backendAlerts = response.data.alerts;
      if (backendAlerts && backendAlerts.length > 0) {
        console.log('⚠️ New alerts from /api/alerts:', backendAlerts);
        setAlerts(backendAlerts.slice(-5));
      } else {
        setAlerts([]);
      }
    }).catch(err => {
      console.error('Error fetching alerts:', err);
    });
  });

  // Also listen for critical alert socket (if your server emits it)
  api.socket.on('critical_alert', (data) => {
    console.warn('🚨 critical_alert:', data);
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('🚨 CRITICAL MOTOR ALERT', {
        body: data.message,
        icon: '/alert-icon.png'
      });
    }
  });

  // Load initial historical data and initial alerts (so UI doesn't wait for socket)
  api.getHistory().then(response => {
    const history = response.data.slice(-20).map(item => ({
      time: new Date(item.timestamp).toLocaleTimeString(),
      temperature: item.temperature,
      vibration: item.vibration,
      current: item.current,
      speed: item.speed
    }));
    setHistoricalData(history);
  }).catch(err => console.error('history fetch error', err));

  // FETCH initial alerts on mount so the UI shows current alerts even if socket hasn't emitted yet
  api.getAlerts().then((response) => {
    const backendAlerts = response.data.alerts;
    if (backendAlerts && backendAlerts.length > 0) {
      console.log('⚠️ Initial alerts loaded:', backendAlerts);
      setAlerts(backendAlerts.slice(-5));
    } else {
      setAlerts([]);
    }
  }).catch(err => console.error('alerts fetch error', err));

  // Ask for notification permission once
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission();
  }

  return () => {
    // remove listeners to avoid duplicates if component unmounts
    api.socket.off('connect');
    api.socket.off('disconnect');
    api.socket.off('connect_error');
    api.socket.off('motor_data');
    api.socket.off('critical_alert');
    // Do not call api.socket.disconnect() if other components might use same socket.
    // If you want fully isolated sockets per-component call socket.disconnect()
  };
}, []);



  const StatusCard = ({ title, value, unit, icon:Icon, status = 'normal', threshold }) => {
    return (
      <div className={`status-card status-card-${status}`}>
        <div className="status-card-header">
          <div className="status-card-title-wrapper">
            <div className={`status-icon status-icon-${status}`}>
              <Icon className="icon" />
            </div>
            <h3 className="status-card-title">{title}</h3>
          </div>
          <div className={`status-indicator status-indicator-${status}`}></div>
        </div>
        <div className="status-card-value">
          <span className="value-number">{typeof value === 'number' ? value.toFixed(1) : value}</span>
          <span className="value-unit">{unit}</span>
        </div>
        {threshold && (
          <div className="status-card-threshold">
            Threshold: {threshold}
          </div>
        )}
      </div>
    );
  };

  const AlertCard = ({ alert }) => {
    return (
      <div className={`alert-card alert-${alert.level.toLowerCase()}`}>
        <div className="alert-content">
          <AlertTriangle className="alert-icon" />
          <div className="alert-details">
            <div className="alert-header">
              <span className="alert-type">{alert.type}</span>
              <span className="alert-level">{alert.level}</span>
            </div>
            <p className="alert-message">{alert.message}</p>
            {alert.value && (
              <p className="alert-value">Value: {alert.value}</p>
            )}
          </div>
        </div>
      </div>
    );
  };

  const getStatusBadge = () => {
    if (motorData.status === 'FAILURE_LIKELY') {
      return (
        <div className="status-badge status-badge-critical">
          <AlertTriangle className="badge-icon" />
          <span className="badge-text">FAILURE LIKELY</span>
        </div>
      );
    } else if (motorData.alerts.length > 0) {
      return (
        <div className="status-badge status-badge-warning">
          <AlertTriangle className="badge-icon" />
          <span className="badge-text">WARNING</span>
        </div>
      );
    }
    return (
      <div className="status-badge status-badge-normal">
        <CheckCircle className="badge-icon" />
        <span className="badge-text">NORMAL OPERATION</span>
      </div>
    );
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-content">
          <div className="header-text">
            <h1 className="dashboard-title">Motor Monitoring Dashboard</h1>
            <p className="dashboard-subtitle">Real-time predictive maintenance system</p>
          </div>
          <div className="header-status">
            {getStatusBadge()}
            <div className="connection-indicator">
              <div className={`connection-dot ${isConnected ? 'connected' : 'disconnected'}`}></div>
              <span className="connection-text">{isConnected ? 'Connected' : 'Disconnected'}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Stats Grid */}
      <div className="stats-grid">
        <StatusCard
          title="Temperature"
          value={motorData.temperature}
          unit="°C"
          icon={Thermometer}
          status={motorData.temperature > 85 ? 'warning' : 'normal'}
          threshold="85°C"
        />
        <StatusCard
          title="Vibration"
          value={motorData.vibration}
          unit="mm/s"
          icon={Activity}
          status={motorData.vibration > 3.0 ? 'warning' : 'normal'}
          threshold="3.0 mm/s"
        />
        <StatusCard
          title="Current"
          value={motorData.current}
          unit="A"
          icon={Zap}
          status={motorData.current > 15 ? 'warning' : 'normal'}
          threshold="15A"
        />
        <StatusCard
          title="Speed"
          value={motorData.speed}
          unit="RPM"
          icon={Gauge}
          status={motorData.speed < 1200 ? 'warning' : 'normal'}
          threshold="1200 RPM"
        />
      </div>

      {/* Charts and Alerts Row */}
      <div className="charts-alerts-row">
        {/* Temperature Chart */}
        <div className="chart-container chart-large">
          <h2 className="chart-title">Temperature Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={historicalData}>
              <defs>
                <linearGradient id="colorTemp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="time" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
              <Area type="monotone" dataKey="temperature" stroke="#ef4444" fillOpacity={1} fill="url(#colorTemp)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Alerts Panel */}
        <div className="alerts-panel">
          <div className="alerts-header">
            <h2 className="alerts-title">Active Alerts</h2>
            <Bell className="bell-icon" />
          </div>
          <div className="alerts-list">
            {alerts.length === 0 ? (
              <div className="no-alerts">
                <CheckCircle className="no-alerts-icon" />
                <p className="no-alerts-text">No active alerts</p>
                <p className="no-alerts-subtext">System operating normally</p>
              </div>
            ) : (
              alerts.map((alert, idx) => (
                <AlertCard key={idx} alert={alert} />
              ))
            )}
          </div>
        </div>
      </div>

      {/* Multi-parameter Charts */}
      <div className="multi-chart-grid">
        <div className="chart-container">
          <h2 className="chart-title">Vibration & Current</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={historicalData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="time" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
              <Legend />
              <Line type="monotone" dataKey="vibration" stroke="#8b5cf6" strokeWidth={2} dot={false} name="Vibration (mm/s)" />
              <Line type="monotone" dataKey="current" stroke="#3b82f6" strokeWidth={2} dot={false} name="Current (A)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h2 className="chart-title">Motor Speed</h2>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={historicalData}>
              <defs>
                <linearGradient id="colorSpeed" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis dataKey="time" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip contentStyle={{ backgroundColor: '#1f2937', border: 'none', borderRadius: '8px', color: '#fff' }} />
              <Area type="monotone" dataKey="speed" stroke="#10b981" fillOpacity={1} fill="url(#colorSpeed)" strokeWidth={2} name="Speed (RPM)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Additional Info Cards */}
      <div className="info-cards-grid">
        <div className="info-card">
          <h3 className="info-card-title">Prediction Status</h3>
          <div className="prediction-content">
            <div className="confidence-section">
              <div className="confidence-header">
                <span className="confidence-label">Confidence</span>
                <span className="confidence-value">{(motorData.prediction_confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className={`progress-fill ${motorData.prediction_confidence > 0.9 ? 'progress-high' : 'progress-medium'}`}
                  style={{ width: `${motorData.prediction_confidence * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="model-status">
              <p className="model-status-label">ML Model Status</p>
              <p className="model-status-value">Active & Running</p>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3 className="info-card-title">Motor Parameters</h3>
          <div className="parameters-list">
            <div className="parameter-item">
              <span className="parameter-label">Torque</span>
              <span className="parameter-value">{motorData.torque.toFixed(1)} Nm</span>
            </div>
            <div className="parameter-item">
              <span className="parameter-label">Tool Wear</span>
              <span className="parameter-value">{motorData.tool_wear} min</span>
            </div>
            <div className="parameter-item">
              <span className="parameter-label">Power</span>
              <span className="parameter-value">{(motorData.torque * motorData.speed * 2 * Math.PI / 60 / 1000).toFixed(2)} kW</span>
            </div>
          </div>
        </div>

        <div className="info-card">
          <h3 className="info-card-title">System Info</h3>
          <div className="parameters-list">
            <div className="parameter-item">
              <span className="parameter-label">Uptime</span>
              <span className="parameter-value">99.4%</span>
            </div>
            <div className="parameter-item">
              <span className="parameter-label">Data Points</span>
              <span className="parameter-value">{historicalData.length}</span>
            </div>
            <div className="parameter-item">
              <span className="parameter-label">Last Update</span>
              <span className="parameter-value">{new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MotorMonitoringDashboard;