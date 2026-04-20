import { useState, useEffect } from "react";
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from "react-native";
import { useUser } from "../../context/UserContext";
import { getTodayLog, updateDailyLog } from "../../services/api";

export default function DailyScreen() {
  const { userId } = useUser();
  const [log, setLog] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dayClosed, setDayClosed] = useState(false);

  const [trainingComplete, setTrainingComplete] = useState(false);
  const [nutritionComplete, setNutritionComplete] = useState(false);
  const [cardioComplete, setCardioComplete] = useState(false);
  const [stepsComplete, setStepsComplete] = useState(false);
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (userId) loadTodayLog();
  }, [userId]);

  const loadTodayLog = async () => {
    setLoading(true);
    const data = await getTodayLog(userId);
    setLog(data);
    if (data.status === "completed") setDayClosed(true);
    setLoading(false);
  };

  const handleCloseDay = async () => {
    const allComplete = trainingComplete && nutritionComplete && cardioComplete && stepsComplete;

    const perfectMessages = [
      "All boxes checked. You're a machine! 🔥",
      "Perfect day. This is what separates you from the rest.",
      "Every box checked. That's a locked in athlete right there.",
      "Full send today. Keep that energy tomorrow.",
      "That's what discipline looks like. Well done."
    ];

    const partialMessages = [
      "Keep it up. Tomorrow is another shot.",
      "Progress over perfection. You showed up.",
      "Not perfect, but you tracked it. That matters.",
      "One day at a time. Come back stronger tomorrow.",
      "Consistency beats intensity. Keep going."
    ];

    const messages = allComplete ? perfectMessages : partialMessages;
    const randomMessage = messages[Math.floor(Math.random() * messages.length)];

    const result = await updateDailyLog(log.id, {
      training_complete: trainingComplete,
      nutrition_complete: nutritionComplete,
      cardio_complete: cardioComplete,
      steps_complete: stepsComplete,
      is_adherent: allComplete,
      notes: notes,
      status: "completed"
    });

    if (result.status === "completed") {
      setDayClosed(true);
      Alert.alert(
        allComplete ? "Perfect Day! 🔥" : "Day Logged 💪",
        randomMessage
      );
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text style={styles.text}>Loading your day...</Text>
      </View>
    );
  }

  const today = new Date().toLocaleDateString("en-US", { weekday: "long", month: "long", day: "numeric" });

  return (
    <ScrollView style={styles.scroll} contentContainerStyle={styles.content}>
      <Text style={styles.date}>{today}</Text>
      <Text style={styles.session}>
        {log?.training_session ? `💪 ${log.training_session} Day` : "📋 No session scheduled"}
      </Text>

      {dayClosed && (
        <View style={styles.closedBanner}>
          <Text style={styles.closedBannerText}>✅ Day Complete</Text>
        </View>
      )}

      <Text style={styles.sectionHeader}>Today's Checklist</Text>

      <TouchableOpacity style={styles.checkRow} onPress={() => !dayClosed && setTrainingComplete(!trainingComplete)}>
        <Text style={styles.checkbox}>{trainingComplete ? "✅" : "⬜"}</Text>
        <Text style={styles.checkLabel}>Training session completed</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.checkRow} onPress={() => !dayClosed && setNutritionComplete(!nutritionComplete)}>
        <Text style={styles.checkbox}>{nutritionComplete ? "✅" : "⬜"}</Text>
        <Text style={styles.checkLabel}>Hit nutrition targets</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.checkRow} onPress={() => !dayClosed && setCardioComplete(!cardioComplete)}>
        <Text style={styles.checkbox}>{cardioComplete ? "✅" : "⬜"}</Text>
        <Text style={styles.checkLabel}>Cardio done</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.checkRow} onPress={() => !dayClosed && setStepsComplete(!stepsComplete)}>
        <Text style={styles.checkbox}>{stepsComplete ? "✅" : "⬜"}</Text>
        <Text style={styles.checkLabel}>Hit step goal</Text>
      </TouchableOpacity>

      <Text style={styles.targets}>
        🎯 Targets: {log?.target_calories} kcal · {log?.target_protein}g protein
      </Text>

      <TouchableOpacity
        style={[styles.closeButton, dayClosed && styles.closeButtonDone]}
        onPress={!dayClosed ? handleCloseDay : undefined}
      >
        <Text style={styles.closeButtonText}>
          {dayClosed ? "✓ Day Closed" : "Close the Day"}
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: "#000" },
  content: { padding: 24, paddingTop: 60 },
  container: { flex: 1, backgroundColor: "#000", justifyContent: "center", alignItems: "center" },
  text: { color: "#fff" },
  date: { color: "#888", fontSize: 16, marginBottom: 4 },
  session: { color: "#fff", fontSize: 28, fontWeight: "800", marginBottom: 24 },
  closedBanner: { backgroundColor: "#1a3a0a", borderRadius: 10, padding: 12, alignItems: "center", marginBottom: 24 },
  closedBannerText: { color: "#4caf50", fontSize: 16, fontWeight: "700" },
  sectionHeader: { color: "#888", fontSize: 12, fontWeight: "600", letterSpacing: 1, marginBottom: 16, textTransform: "uppercase" },
  checkRow: { flexDirection: "row", alignItems: "center", marginBottom: 20 },
  checkbox: { fontSize: 24, marginRight: 12 },
  checkLabel: { color: "#fff", fontSize: 16 },
  targets: { color: "#666", fontSize: 14, marginTop: 8, marginBottom: 32 },
  closeButton: { backgroundColor: "#555", borderRadius: 12, padding: 18, alignItems: "center" },
  closeButtonDone: { backgroundColor: "#2D5016" },
  closeButtonText: { color: "#fff", fontSize: 16, fontWeight: "700" }
});