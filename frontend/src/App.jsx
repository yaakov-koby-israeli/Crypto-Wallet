import { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Login } from "./views/Login";
import { Register } from "./views/Register";
import { Dashboard } from "./views/Dashboard";
import { ThemeToggle } from "./components/ui/Components";
import { useAuth } from "./controllers/useAuth";
import { useWallet } from "./controllers/useWallet";

const PrivateRoute = ({ isAuthed, children }) =>
  isAuthed ? children : <Navigate to="/login" replace />;

export default function App() {
  const [theme, setTheme] = useState(() => localStorage.getItem("theme") || "dark");
  const auth = useAuth();
  const wallet = useWallet();

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark");
    document.body.classList.toggle("light", theme === "light");
    localStorage.setItem("theme", theme);
  }, [theme]);

  const handleLogin = async (credentials) => {
    const ok = await auth.login(credentials);
    if (ok) {
      await wallet.loadTransactions();
    }
  };

  const handleRegister = async (payload) => auth.register(payload);

  const handleSetup = (pk) => wallet.setupAccount(pk);
  const handleTransfer = (data) => wallet.transfer(data);

  return (
    <BrowserRouter>
      <div className="fixed right-4 top-4 z-50">
        <ThemeToggle
          theme={theme}
          onToggle={() => setTheme(theme === "dark" ? "light" : "dark")}
        />
      </div>
      <Routes>
        <Route
          path="/login"
          element={<Login onLogin={handleLogin} loading={auth.loading} error={auth.error} />}
        />
        <Route
          path="/register"
          element={
            <Register onRegister={handleRegister} loading={auth.loading} error={auth.error} />
          }
        />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute isAuthed={!!auth.token}>
              <Dashboard
                user={auth.user}
                balance={wallet.balance}
                accountId={wallet.accountId}
                transactions={wallet.transactions}
                onSetup={handleSetup}
                onTransfer={handleTransfer}
                loading={wallet.loading}
                error={wallet.error}
              />
            </PrivateRoute>
          }
        />
        <Route path="*" element={<Navigate to={auth.token ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </BrowserRouter>
  );
}
