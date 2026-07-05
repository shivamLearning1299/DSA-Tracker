import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const apiClient = axios.create({ baseURL });

let accessToken: string | null = null;
let refreshInFlight: Promise<string | null> | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getStoredRefreshToken(): string | null {
  return localStorage.getItem("refresh_token");
}

export function setStoredRefreshToken(token: string | null) {
  if (token) {
    localStorage.setItem("refresh_token", token);
  } else {
    localStorage.removeItem("refresh_token");
  }
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = getStoredRefreshToken();
  if (!refresh) return null;

  if (!refreshInFlight) {
    refreshInFlight = axios
      .post(`${baseURL}/api/auth/token/refresh/`, { refresh })
      .then((res) => {
        const newAccess = res.data.access as string;
        setAccessToken(newAccess);
        return newAccess;
      })
      .catch(() => {
        setAccessToken(null);
        setStoredRefreshToken(null);
        return null;
      })
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

apiClient.interceptors.request.use((config) => {
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const newAccess = await refreshAccessToken();
      if (newAccess) {
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return apiClient(originalRequest);
      }
    }
    return Promise.reject(error);
  }
);

export { refreshAccessToken };
