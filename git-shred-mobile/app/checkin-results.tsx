import { View, Text, StyleSheet, ScrollView, TouchableOpacity } from "react-native";
import { useLocalSearchParams, router } from "expo-router";

export default function CheckinResults() {
  const { messages, userId } = useLocalSearchParams();
  const msgs = JSON.parse(messages as string);

  const getStyle = (type: string) => {
    if (type === "error") return styles.error;
    if (type === "warning") return styles.warning;
    if (type === "success") return styles.success;
    return styles.info;
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>💪 Your Recommendation</Text>
      <Text style={styles.subtitle}>Based on this week's data</Text>

      {msgs.map((msg: [string, string], i: number) => (
        <View key={i} style={[styles.card, getStyle(msg[0])]}>
          <Text style={styles.cardText}>{msg[1]}</Text>
        </View>
      ))}

      <TouchableOpacity style={styles.button} onPress={() => router.push({ pathname: "/dashboard", params: { userId }})}>
        <Text style={styles.buttonText}>Back to Dashboard</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: "#F8F9FA", alignItems: "center", padding: 24, paddingTop: 60 },
  title: { fontSize: 32, fontWeight: "700", color: "#1A1A1A", marginBottom: 4 },
  subtitle: { fontSize: 16, color: "#6B7280", marginBottom: 32 },
  card: { width: "100%", borderRadius: 12, padding: 16, marginBottom: 10 },
  cardText: { fontSize: 14, fontWeight: "500", color: "#1A1A1A" },
  error: { backgroundColor: "#FEE2E2", borderColor: "#FCA5A5", borderWidth: 1 },
  warning: { backgroundColor: "#FEF3C7", borderColor: "#FCD34D", borderWidth: 1 },
  success: { backgroundColor: "#DCFCE7", borderColor: "#86EFAC", borderWidth: 1 },
  info: { backgroundColor: "#DBEAFE", borderColor: "#93C5FD", borderWidth: 1 },
  button: { width: "100%", backgroundColor: "#2D5016", borderRadius: 12, padding: 16, alignItems: "center", marginTop: 24, marginBottom: 40 },
  buttonText: { color: "white", fontSize: 16, fontWeight: "600" }
});
