import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { createUser } from "../services/api";

export default function CreatePlan() {
  const { email } = useLocalSearchParams();
  const [age, setAge] = useState("");
  const [sex, setSex] = useState(1);
  const [heightIn, setHeightIn] = useState("");
  const [weight, setWeight] = useState("");
  const [activityLevel, setActivityLevel] = useState(3);
  const [goalWeight, setGoalWeight] = useState("");
  const [weeksToGoal, setWeeksToGoal] = useState("");
  const [checkinDay, setCheckinDay] = useState(1);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!age || !heightIn || !weight || !goalWeight || !weeksToGoal) {
      Alert.alert("Please fill in all fields");
      return;
    }
    setLoading(true);
    const result = await createUser({
      email,
      age: parseInt(age),
      sex,
      height_in: parseInt(heightIn),
      weight: parseFloat(weight),
      activity_level: activityLevel,
      goal_weight: parseFloat(goalWeight),
      weeks_to_goal: parseInt(weeksToGoal),
      checkin_day: checkinDay
    });
    setLoading(false);

    if (result.user_id) {
      router.push({ pathname: "/plan-created", params: { plan: JSON.stringify(result.plan), userId: result.user_id }});
    } else {
      Alert.alert("Error creating plan", result.detail || "Please try again");
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>💪 Git Shred</Text>
      <Text style={styles.subtitle}>Let's build your plan</Text>

      <Text style={styles.label}>Age</Text>
      <TextInput style={styles.input} placeholder="Age" value={age} onChangeText={setAge} keyboardType="numeric" />

      <Text style={styles.label}>Sex</Text>
      <View style={styles.row}>
        <TouchableOpacity style={[styles.optionBtn, sex === 1 && styles.optionBtnActive]} onPress={() => setSex(1)}>
          <Text style={[styles.optionText, sex === 1 && styles.optionTextActive]}>Male</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.optionBtn, sex === 2 && styles.optionBtnActive]} onPress={() => setSex(2)}>
          <Text style={[styles.optionText, sex === 2 && styles.optionTextActive]}>Female</Text>
        </TouchableOpacity>
      </View>

      <Text style={styles.label}>Height (inches)</Text>
      <TextInput style={styles.input} placeholder="Height in inches" value={heightIn} onChangeText={setHeightIn} keyboardType="numeric" />

      <Text style={styles.label}>Current Weight (lbs)</Text>
      <TextInput style={styles.input} placeholder="Current weight" value={weight} onChangeText={setWeight} keyboardType="numeric" />

      <Text style={styles.label}>Goal Weight (lbs)</Text>
      <TextInput style={styles.input} placeholder="Goal weight" value={goalWeight} onChangeText={setGoalWeight} keyboardType="numeric" />

      <Text style={styles.label}>Timeframe (weeks, 0 = no timeframe)</Text>
      <TextInput style={styles.input} placeholder="Weeks to goal" value={weeksToGoal} onChangeText={setWeeksToGoal} keyboardType="numeric" />

      <Text style={styles.label}>Activity Level</Text>
      {[
        [1, "Sedentary (<5k steps)"],
        [2, "Lightly Active (5-7.5k)"],
        [3, "Moderately Active (7.5-10k)"],
        [4, "Very Active (10-12.5k)"],
        [5, "Extremely Active (12.5k+)"]
      ].map(([val, label]) => (
        <TouchableOpacity key={val} style={[styles.optionBtn, activityLevel === val && styles.optionBtnActive, { width: "100%", marginBottom: 8 }]} onPress={() => setActivityLevel(val)}>
          <Text style={[styles.optionText, activityLevel === val && styles.optionTextActive]}>{label}</Text>
        </TouchableOpacity>
      ))}

      <Text style={styles.label}>Weekly Check-in Day</Text>
      <View style={styles.row}>
        {[["M",1],["T",2],["W",3],["Th",4],["F",5],["Sa",6],["Su",7]].map(([day, val]) => (
          <TouchableOpacity key={val} style={[styles.dayBtn, checkinDay === val && styles.optionBtnActive]} onPress={() => setCheckinDay(val)}>
            <Text style={[styles.optionText, checkinDay === val && styles.optionTextActive]}>{day}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <TouchableOpacity style={styles.button} onPress={handleSubmit}>
        <Text style={styles.buttonText}>{loading ? "Creating..." : "Create My Plan"}</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: "#F8F9FA", alignItems: "center", padding: 24, paddingTop: 60 },
  title: { fontSize: 32, fontWeight: "700", color: "#1A1A1A", marginBottom: 4 },
  subtitle: { fontSize: 16, color: "#6B7280", marginBottom: 32 },
  label: { alignSelf: "flex-start", fontSize: 14, fontWeight: "600", color: "#374151", marginBottom: 6, marginTop: 12 },
  input: { width: "100%", backgroundColor: "white", borderWidth: 1, borderColor: "#E5E7EB", borderRadius: 12, padding: 14, fontSize: 16, marginBottom: 4 },
  row: { flexDirection: "row", gap: 8, marginBottom: 4, flexWrap: "wrap" },
  optionBtn: { paddingVertical: 10, paddingHorizontal: 16, borderRadius: 10, borderWidth: 1, borderColor: "#E5E7EB", backgroundColor: "white" },
  optionBtnActive: { backgroundColor: "#2D5016", borderColor: "#2D5016" },
  optionText: { color: "#374151", fontWeight: "500" },
  optionTextActive: { color: "white" },
  dayBtn: { paddingVertical: 10, paddingHorizontal: 10, borderRadius: 10, borderWidth: 1, borderColor: "#E5E7EB", backgroundColor: "white" },
  button: { width: "100%", backgroundColor: "#2D5016", borderRadius: 12, padding: 16, alignItems: "center", marginTop: 32, marginBottom: 40 },
  buttonText: { color: "white", fontSize: 16, fontWeight: "600" }
});
