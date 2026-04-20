import { Tabs } from "expo-router";
import { Ionicons } from "@expo/vector-icons";

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: {
          backgroundColor: "#000000",
          borderTopColor: "#222222",
        },
        tabBarActiveTintColor: "#ffffff",
        tabBarInactiveTintColor: "#666666",
      }}
    >
      <Tabs.Screen
        name="checkin"
        options={{
          title: "Check-in",
          tabBarIcon: ({ color }) => (
            <Ionicons name="calendar-outline" size={24} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="progress"
        options={{
          title: "Progress",
          tabBarIcon: ({ color }) => (
            <Ionicons name="trending-up-outline" size={24} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="daily"
        options={{
          title: "Daily",
          tabBarIcon: ({ color }) => (
            <Ionicons name="checkmark-circle-outline" size={24} color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: "Profile",
          tabBarIcon: ({ color }) => (
            <Ionicons name="person-outline" size={24} color={color} />
          ),
        }}
      />
    </Tabs>
  );
}