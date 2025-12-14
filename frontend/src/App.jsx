import { useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Login } from "./views/Login";
import { Register } from "./views/Register";
import { Home } from "./views/Home";
import { Dashboard } from "./views/Dashboard";
import { useAuth } from "./controllers/useAuth";
import { useWallet } from "./controllers/useWallet";

const PrivateRoute = ({ isAuthed, children }) =>
  isAuthed ? children : <Navigate to="/login" replace />;

export default function App() {
  const auth = useAuth();
  const wallet = useWallet();

  useEffect(() => {
    document.documentElement.classList.add("dark");
    document.body.classList.remove("light");
    document.documentElement.style.colorScheme = "dark";
    localStorage.setItem("theme", "dark");
  }, []);

  const handleLogin = async (credentials) => {
    const ok = await auth.login(credentials);
    if (ok) {
      await wallet.loadAccount();
      await wallet.loadTransactions();
    }
    return ok;
  };

  const handleRegister = async (payload) => auth.register(payload);

  const handleSetup = (pk) => wallet.setupAccount(pk);
  const handleTransfer = (data) => wallet.transfer(data);
  const handleLogout = () => {
    auth.logout();
    wallet.resetWallet();
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
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
                ethUsdRate={wallet.ethUsdRate}
                onLogout={handleLogout}
                onSetup={handleSetup}
                onTransfer={handleTransfer}
                onRefreshAccount={wallet.loadAccount}
                onRefreshTransactions={wallet.loadTransactions}
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
