import React, { useEffect, useState } from "react";
import { View, Text, StyleSheet, ScrollView } from "react-native";
import { io, Socket } from "socket.io-client";

// Define the shape of the motor data
interface MotorData {
  temperature: number;
  vibration: number;
  status: string;
}

// Define alert shape
interface Alert {
  message: string;
}

// Define socket event types (optional)
interface ServerToClientEvents {
  motor_data: (data: MotorData) => void;
  critical_alert: (data: { alerts: Alert[] }) => void;
}

export default function Dashboard() {
  const [data, setData] = useState<MotorData>({
    temperature: 0,
    vibration: 0,
    status: "Normal",
  });
  const [alerts, setAlerts] = useState<Alert[]>([]);

  useEffect(() => {
    // 👇 Replace with your IPv4 address
    const socket: Socket<ServerToClientEvents> = io("http://192.168.111.1:5000");

    socket.on("connect", () => {
      console.log("✅ Connected to backend");
    });

    socket.on("motor_data", (incoming) => {
      setData(incoming);
    });

    socket.on("critical_alert", (alertData) => {
      setAlerts(alertData.alerts || []);
    });

    return () => {
      socket.disconnect();
    };
  }, []);

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Motor Monitoring Dashboard</Text>

      <View style={styles.card}>
        <Text style={styles.label}>Temperature:</Text>
        <Text style={styles.value}>{data.temperature} °C</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Vibration:</Text>
        <Text style={styles.value}>{data.vibration}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Status:</Text>
        <Text
          style={[
            styles.value,
            { color: data.status === "Critical" ? "red" : "green" },
          ]}
        >
          {data.status}
        </Text>
      </View>

      <Text style={styles.subtitle}>Recent Alerts:</Text>
      {alerts.length === 0 ? (
        <Text style={styles.noAlerts}>No alerts</Text>
      ) : (
        alerts.map((a, i) => (
          <View key={i} style={styles.alertCard}>
            <Text style={{ color: "red" }}>{a.message}</Text>
          </View>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    padding: 20,
    backgroundColor: "#f9fafb",
  },
  title: {
    fontSize: 24,
    fontWeight: "bold",
    marginBottom: 20,
    textAlign: "center",
  },
  card: {
    backgroundColor: "#fff",
    padding: 15,
    marginBottom: 10,
    borderRadius: 10,
    elevation: 3,
  },
  label: {
    fontSize: 16,
    color: "#555",
  },
  value: {
    fontSize: 20,
    fontWeight: "bold",
  },
  subtitle: {
    marginTop: 20,
    fontSize: 18,
    fontWeight: "bold",
  },
  noAlerts: {
    color: "gray",
    marginTop: 5,
  },
  alertCard: {
    backgroundColor: "#ffe5e5",
    padding: 10,
    borderRadius: 8,
    marginTop: 5,
  },
});
