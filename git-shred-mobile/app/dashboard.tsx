import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { useLocalSearchParams, router } from "expo-router";

export default function Dashboard() {
  const { userId } = useLocalSearchParams();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>💪 Git Shred</Text>
      <Text style={styles.subtitle}>Welcome back!</Text>

      <TouchableOpacity style={styles.button} onPress={() => router.push({ pathname: "/checkin", params: { userId }})}>
        <Text style={styles.buttonText}>📋 Weekly Check-in</Text>
      </TouchableOpacity>

      <TouchableOpacity style={[styles.button, styles.secondary]}>
        <Text style={styles.buttonText}>📊 Progress (Coming Soon)</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F8F9FA", alignItems: "center", justifyContent: "center", padding: 24 },
  title: { fontSize: 36, fontWeight: "700", color: "#1A1A1A", marginBottom: 8 },
  subtitle: { fontSize: 16, color: "#6B7280", marginBottom: 48 },
  button: { width: "100%", backgroundColor: "#2D5016", borderRadius: 12, padding: 16, alignItems: "center", marginBottom: 12 },
  secondary: { backgroundColor: "#6B7280" },
  buttonText: { color: "white", fontSize: 16, fontWeight: "600" }
});
