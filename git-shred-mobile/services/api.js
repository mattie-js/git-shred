const BASE_URL = "https://git-shred-production.up.railway.app";

export const loginUser = async (email) => {
  const response = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  });
  return response.json();
};

export const createUser = async (userData) => {
  const response = await fetch(`${BASE_URL}/create-user`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData)
  });
  return response.json();
};

export const submitCheckin = async (checkinData) => {
  const response = await fetch(`${BASE_URL}/checkin`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(checkinData)
  });
  return response.json();
};

export const getProgress = async (userId) => {
  const response = await fetch(`${BASE_URL}/progress/${userId}`);
  return response.json();
};

export const getTodayLog = async (userId) => {
  const response = await fetch(`${BASE_URL}/daily-log/today/${userId}`);
  return response.json();
};

export const updateDailyLog = async (logId, updates) => {
  const response = await fetch(`${BASE_URL}/daily-log/${logId}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(updates)
  });
  return response.json();
};

export const getTrainingTemplate = async (userId) => {
  const response = await fetch(`${BASE_URL}/training-template/${userId}`);
  return response.json();
};

export const saveTrainingTemplate = async (userId, schedule) => {
  const response = await fetch(`${BASE_URL}/training-template/${userId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ schedule })
  });
  return response.json();
};