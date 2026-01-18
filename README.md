# 🔧 Predictive Maintenance of Industrial Motors

## 📌 Overview
Predictive Maintenance of Industrial Motors is an integrated **hardware–software system** designed to **predict motor faults before failure occurs**.  
The system continuously monitors key parameters such as **current, vibration, temperature, and humidity**, analyzes them against predefined thresholds, and generates **real-time alerts** to prevent unexpected breakdowns.

This project demonstrates the application of **IoT, embedded systems, data processing, and full-stack development** in an industrial use case.

---

## 🎯 Objectives
- Monitor real-time motor health parameters
- Predict abnormal operating conditions before failure
- Classify system states as **Normal, Critical, or Alert**
- Provide a real-time dashboard for visualization
- Generate alerts when thresholds are exceeded

---

## 🛠️ Hardware Components
- **Microcontroller:** STM32 Nucleo F446ZE  
- **Sensors Used:**
  - ACS712 – Current Sensor
  - ADXL345 – Vibration Sensor
  - DHT22 – Temperature & Humidity Sensor
- **Development Environment:** Arduino IDE

---

## 💻 Software & Technology Stack

### 🔹 Backend
- Python
- Real-time data processing
- Threshold-based condition evaluation

### 🔹 Frontend
- React Native
- HTML, CSS, JavaScript
- Dashboard for live data visualization

### 🔹 Mobile Application
- Expo Go (for real-time mobile display)

### 🔹 Databases
- MySQL
- Kaggle (for dataset reference and experimentation)

### 🔹 Tools
- Git & GitHub
- Arduino IDE

---

## ⚙️ System Architecture
1. Sensors collect real-time motor parameters  
2. STM32 microcontroller reads sensor values  
3. Data is transmitted via Arduino Serial Monitor  
4. Backend processes and evaluates data using Python  
5. Frontend dashboard displays real-time values  
6. Alerts are triggered when thresholds are crossed  

---

## 🚦 Alert Mechanism
The system categorizes motor condition into three states:
- **Normal:** Parameters within safe limits
- **Critical:** Parameters approaching unsafe thresholds
- **Alert:** Parameters exceeding critical thresholds → alert generated

---

## 📊 Features
- Real-time monitoring of industrial motor parameters
- Threshold-based fault prediction
- Live dashboard visualization
- Mobile-friendly interface
- Scalable architecture for industrial use

---

## 🚀 Future Enhancements
- Integration of Machine Learning models for advanced prediction
- Cloud-based data storage and analytics
- Automated maintenance scheduling
- SMS/Email alert notifications
- Support for multiple motors

---

## 📚 Learning Outcomes
- Hands-on experience with embedded systems
- IoT sensor integration
- Full-stack application development
- Real-time data handling
- Industrial predictive maintenance concepts

---

## 👩‍💻 Author
**Shravani Prashant Deshpande**  
Final-year Engineering Student  
Upcoming Analyst at Capgemini  

📌 GitHub: [https://github.com/ShravaniPD21](https://github.com/ShravaniPD21)
