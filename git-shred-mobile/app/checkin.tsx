import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, ScrollView, Alert } from "react-native";
import { useLocalSearchParams, router } from "expo-router";
import { submitCheckin } from "../services/api";

export default function Checkin() {
  const { userId } = useLocalSearchParams();
  const [avgWeight, setAvgWeight] = useState("");
  const [daysTracked, setDaysTracked] = useState("");
  const [avgSteps, setAvgSteps] = useState("");
  const [strength, setStrength] = useState(2);
  const [fatigue, setFatigue] = useState(5);
  const [daysAdherent, setDaysAdherent] = useState("");
  const [caloriesOver, setCaloriesOver] = useState("");
  const [offTheRails, setOffTheRails] = useState(0);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!avgWeight || !daysTracked || !avgSteps || !daysAdherent) {
      Alert.alert("Please fill in all fields");
      return;
    }
    setLoading(true);
    const result = await submitCheckin({
      user_id: parseInt(userId),
      avg_weight_lbs: parseFloat(avgWeight),
      days_tracked: parseInt(daysTracked),
      avg_step_count: parseInt(avgSteps),
      strength_subj: strength,
      fatigue_subj: fatigue,
      days_adherent: parseInt(daysAdherent),
      calories_over: caloriesOver ? parseFloat(caloriesOver) : null,
      off_the_rails: offTheRails
    });
    setLoading(false);

    if (result.messages) {
      router.push({ pathname: "/checkin-results", params: { messages: JSON.stringify(result.messages), userId }});
    } else {
      Alert.alert("Error", "Something went wrong. Please try again.");
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>💪 Weekly Check-in</Text>
      <Text style={styles.subtitle}>How did this week go?</Text>

      <Text style={styles.label}>Average Weight This Week (lbs)</Text>
      <TextInput style={styles.input} placeholder="e.g. 188.5" value={avgWeight} onChangeText={setAvgWeight} keyboardType="numeric" />

      <Text style={styles.label}>Days You Tracked Weight (1-7)</Text>
      <TextInput style={styles.input} placeholder="e.g. 5" value={daysTracked} onChangeText={setDaysTracked} keyboardType="numeric" />

      <Text style={styles.label}>Average Daily Steps</Text>
      <TextInput style={styles.input} placeholder="e.g. 8000" value={avgSteps} onChangeText={setAvgSteps} keyboardType="numeric" />

      <Text style={styles.label}>Strength This Week</Text>
      {[[1, "Getting Stronger"], [2, "Maintaining"], [3, "Getting Weaker"]].map(([val, label]) => (
        <TouchableOpacity key={val} style={[styles.optionBtn, strength === val && styles.optionBtnActive, { width: "100%", marginBottom: 8 }]} onPress={() => setStrength(val)}>
          <Text style={[styles.optionText, strength === val && styles.optionTextActive]}>{label}</Text>
        </TouchableOpacity>
      ))}

      <Text style={styles.label}>Fatigue This Week (1-10)</Text>
      <View style={styles.row}>
        {[1,2,3,4,5,6,7,8,9,10].map(val => (
          <TouchableOpacity key={val} style={[styles.dayBtn, fatigue === val && styles.optionBtnActive]} onPress={() => setFatigue(val)}>
            <Text style={[styles.optionText, fatigue === val && styles.optionTextActive]}>{val}</Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>Days Adherent to Plan (0-7)</Text>
      <TextInput style={styles.input} placeholder="e.g. 6" value={daysAdherent} onChangeText={setDaysAdherent} keyboardType="numeric" />

      <Text style={styles.label}>Off Plan Days</Text>
      {[[0, "Fully Adherent"], [1, "Know Calories Over"], [2, "Went Off the Rails"]].map(([val, label]) => (
        <TouchableOpacity key={val} style={[styles.optionBtn, offTheRails === val && styles.optionBtnActive, { width: "100%", marginBottom: 8 }]} onPress={() => setOffTheRails(val)}>
          <Text style={[styles.optionText, offTheRails === val && styles.optionTextActive]}>{label}</Text>
        </TouchableOpacity>
      ))}

      {offTheRails === 1 && (
        <>
          <Text style={styles.label}>Total Calories Over</Text>
          <TextInput style={styles.input} placeholder="e.g. 500" value={caloriesOver} onChangeText={setCaloriesOver} keyboardType="numeric" />
        </>
      )}

      <TouchableOpacity style={styles.button} onPress={handleSubmit}>
        <Text style={styles.buttonText}>{loading ? "Submitting..." : "Submit Check-in"}</Text>
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
  dayBtn: { paddingVertical: 8, paddingHorizontal: 8, borderRadius: 10, borderWidth: 1, borderColor: "#E5E7EB", backgroundColor: "white" },
  button: { width: "100%", backgroundColor: "#2D5016", borderRadius: 12, padding: 16, alignItems: "center", marginTop: 32, marginBottom: 40 },
  buttonText: { color: "white", fontSize: 16, fontWeight: "600" }
});