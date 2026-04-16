import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Alert } from "react-native";
import { loginUser } from "../services/api";
import { router } from "expo-router";


export default function HomeScreen() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
      if (!email) {
        Alert.alert("Please enter your email");
        return;
      }
      setLoading(true);
      const result = await loginUser(email);
      setLoading(false);

      if (result.user_id) {
        router.push({ pathname: "/dashboard", params: { userId: result.user_id }});
      } else {
        router.push({ pathname: "/create-plan", params: { email } });
      }
    };


  return (
    <View style={styles.container}>
      <Text style={styles.title}>💪 Git Shred</Text>
      <Text style={styles.subtitle}>Adaptive Diet Coaching</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Enter your email"
        value={email}
        onChangeText={setEmail}
        keyboardType="email-address"
        autoCapitalize="none"
      />

      <TouchableOpacity style={styles.button} onPress={handleLogin}>
        <Text style={styles.buttonText}>
          {loading ? "Loading..." : "Get Started"}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F8F9FA",
    alignItems: "center",
    justifyContent: "center",
    padding: 24
  },
  title: {
    fontSize: 36,
    fontWeight: "700",
    color: "#1A1A1A",
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: "#6B7280",
    marginBottom: 48
  },
  input: {
    width: "100%",
    backgroundColor: "white",
    borderWidth: 1,
    borderColor: "#E5E7EB",
    borderRadius: 12,
    padding: 16,
    fontSize: 16,
    marginBottom: 16
  },
  button: {
    width: "100%",
    backgroundColor: "#2D5016",
    borderRadius: 12,
    padding: 16,
    alignItems: "center"
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "600"
  }
});