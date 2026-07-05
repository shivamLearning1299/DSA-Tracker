import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useState,
} from "react";

import {
  apiClient,
  getStoredRefreshToken,
  refreshAccessToken,
  setAccessToken,
  setStoredRefreshToken,
} from "../api/client";

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  loginWithGoogle: (credential: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  async function fetchMe() {
    const { data } = await apiClient.get<User>("/api/auth/me/");
    setUser(data);
  }

  useEffect(() => {
    (async () => {
      if (getStoredRefreshToken()) {
        const newAccess = await refreshAccessToken();
        if (newAccess) {
          try {
            await fetchMe();
          } catch {
            setUser(null);
          }
        }
      }
      setIsLoading(false);
    })();
  }, []);

  async function loginWithGoogle(credential: string) {
    const { data } = await apiClient.post("/api/auth/google/", { credential });
    setAccessToken(data.access);
    setStoredRefreshToken(data.refresh);
    setUser(data.user);
  }

  function logout() {
    setAccessToken(null);
    setStoredRefreshToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, loginWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
