import { View, Text, StyleSheet, TouchableOpacity } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { useUser } from "../context/UserContext";

export default function PlanCreated() {
  const { plan, userId } = useLocalSearchParams();
  const { setUserId } = useUser();
  const p = JSON.parse(plan as string);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>💪 Your Plan</Text>
      <Text style={styles.subtitle}>You're all set. Let's get shredded.</Text>

      <View style={styles.card}>
        <Text style={styles.metric}>Daily Calories</Text>
        <Text style={styles.value}>{parseInt(p.cal_rx)} kcal</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.metric}>Protein</Text>
        <Text style={styles.value}>{parseInt(p.protein_rx)}g</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.metric}>Carbs</Text>
        <Text style={styles.value}>{parseInt(p.carb_rx)}g</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.metric}>Fat</Text>
        <Text style={styles.value}>{parseInt(p.fat_rx)}g</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.metric}>TDEE</Text>
        <Text style={styles.value}>{parseInt(p.tdee)} kcal</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.metric}>Goal Weight</Text>
        <Text style={styles.value}>{parseInt(p.goal_weight)} lbs</Text>
      </View>

      <TouchableOpacity style={styles.button} onPress={() => {
        setUserId(Number(userId));
        router.replace({ pathname: "/(tabs)/checkin" });
      }}>
        <Text style={styles.buttonText}>Let's Go 💪</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#F8F9FA", alignItems: "center", justifyContent: "center", padding: 24 },
  title: { fontSize: 32, fontWeight: "700", color: "#1A1A1A", marginBottom: 4 },
  subtitle: { fontSize: 16, color: "#6B7280", marginBottom: 32 },
  card: { width: "100%", backgroundColor: "white", borderRadius: 12, borderWidth: 1, borderColor: "#E5E7EB", padding: 16, marginBottom: 10, flexDirection: "row", justifyContent: "space-between" },
  metric: { fontSize: 14, color: "#6B7280", fontWeight: "500" },
  value: { fontSize: 16, fontWeight: "700", color: "#1A1A1A" },
  button: { width: "100%", backgroundColor: "#2D5016", borderRadius: 12, padding: 16, alignItems: "center", marginTop: 24 },
  buttonText: { color: "white", fontSize: 16, fontWeight: "600" }
});