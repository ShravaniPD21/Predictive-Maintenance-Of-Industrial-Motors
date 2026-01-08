import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# =====================================================
# 1. Dummy feature columns
# =====================================================
feature_columns = [
    'Air temperature [K]',
    'Process temperature [K]',
    'Rotational speed [rpm]',
    'Torque [Nm]',
    'Tool wear [min]',
    'Type_Encoded',
    'Temp_Difference',
    'Temp_Ratio',
    'Process_Temp_C',
    'Air_Temp_C',
    'High_Process_Temp',
    'High_Temp_Diff',
    'Power',
    'Torque_Speed_Ratio',
    'High_Torque',
    'Low_Speed',
    'High_Tool_Wear',
    'Risk_Score'
]
joblib.dump(feature_columns, 'feature_columns.pkl')
print("✅ feature_columns.pkl created.")

# =====================================================
# 2. Dummy scaler (StandardScaler trained on fake data)
# =====================================================
fake_data = np.random.rand(100, len(feature_columns))
scaler = StandardScaler()
scaler.fit(fake_data)
joblib.dump(scaler, 'feature_scaler.pkl')
print("✅ feature_scaler.pkl created.")

# =====================================================
# 3. Dummy model (Logistic Regression trained on fake data)
# =====================================================
model = LogisticRegression()
X = np.random.randn(100, len(feature_columns))
y = np.random.randint(0, 2, 100)
model.fit(X, y)
joblib.dump(model, 'motor_failure_model.pkl')
print("✅ motor_failure_model.pkl created.")

# =====================================================
# 4. Dummy label encoders (for machine types, etc.)
# =====================================================
label_encoders = {
    'Type': {'L': 0, 'M': 1, 'H': 2}
}
joblib.dump(label_encoders, 'label_encoders.pkl')
print("✅ label_encoders.pkl created.")

# =====================================================
# 5. Dummy alert thresholds (same as your THRESHOLDS)
# =====================================================
alert_thresholds = {
    'temperature': {'warning': 85, 'critical': 95},
    'vibration': {'warning': 3.0, 'critical': 4.5},
    'current': {'warning': 15, 'critical': 18},
    'speed_low': {'warning': 1200, 'critical': 1000},
    'torque': {'warning': 50, 'critical': 60},
    'tool_wear': {'warning': 180, 'critical': 220}
}
joblib.dump(alert_thresholds, 'alert_thresholds.pkl')
print("✅ alert_thresholds.pkl created.")

print("\n🎉 All dummy .pkl files created successfully!")
