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
