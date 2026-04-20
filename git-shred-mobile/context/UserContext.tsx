import { createContext, useContext, useState } from "react";

type UserContextType = {
  userId: number | null;
  setUserId: (id: number) => void;
};

const UserContext = createContext<UserContextType>({
  userId: null,
  setUserId: () => {},
});

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [userId, setUserId] = useState<number | null>(null);

  return (
    <UserContext.Provider value={{ userId, setUserId }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}