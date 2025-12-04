import { useEffect, useState, useCallback } from "react";
import jwtDecode from "jwt-decode";
import { walletService } from "../api/walletService";

const TOKEN_KEY = "token";

export function useAuth() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem(TOKEN_KEY) || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const persistToken = useCallback((newToken) => {
    setToken(newToken);
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken);
      const decoded = jwtDecode(newToken);
      setUser({
        username: decoded.sub,
        id: decoded.id,
        role: decoded.role,
        public_key: decoded.public_key,
      });
    } else {
        localStorage.removeItem(TOKEN_KEY);
        setUser(null);
      }
  }, []);

  useEffect(() => {
    if (token) {
      try {
        const decoded = jwtDecode(token);
        setUser({
          username: decoded.sub,
          id: decoded.id,
          role: decoded.role,
          public_key: decoded.public_key,
        });
      } catch (e) {
        persistToken(null);
      }
    }
  }, [token, persistToken]);

  const login = async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const data = await walletService.login(credentials);
      persistToken(data.access_token);
      return true;
    } catch (e) {
      setError(e.response?.data?.detail || "Login failed");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const register = async (payload) => {
    setLoading(true);
    setError(null);
    try {
      await walletService.register(payload);
      return true;
    } catch (e) {
      setError(e.response?.data?.detail || "Registration failed");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => persistToken(null);

  return { user, token, loading, error, login, register, logout };
}
