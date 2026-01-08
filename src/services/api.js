// src/services/api.js
import axios from 'axios';
import { io } from 'socket.io-client';

const API_URL = 'http://192.168.111.1:5000';

// Use polling transport to ensure compatibility with Flask-SocketIO when websocket transport
// isn't available (common when not running eventlet/gevent on the server).
// If you later install eventlet on server side, you can remove `transports` and let socket.io
// auto-negotiate.
const socket = io(API_URL, {
  transports: ['polling'], // force polling to avoid websocket handshake failure
  path: '/socket.io'
});

const api = {
  getStatus: () => axios.get(`${API_URL}/api/status`),
  getHistory: (limit = 100) => axios.get(`${API_URL}/api/history?limit=${limit}`),
  getAlerts: () => axios.get(`${API_URL}/api/alerts`),
  getStatistics: () => axios.get(`${API_URL}/api/statistics`),
  socket
};

export default api;
