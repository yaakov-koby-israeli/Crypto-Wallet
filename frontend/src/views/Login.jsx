import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input, Logo } from "../components/ui/Components";

export const Login = ({ onLogin, loading, error }) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    const ok = await onLogin({ username, password });
    if (ok) {
      navigate("/dashboard");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-dark text-white">
      <div className="w-full max-w-md rounded-2xl border border-white/10 bg-white/5 p-8 shadow-soft backdrop-blur animate-fade-slide">
        <div className="mb-6 flex items-center justify-between">
          <Logo />
          <div className="text-sm text-white/60">Secure Wallet Access</div>
        </div>
        <form className="space-y-4" onSubmit={submit}>
          <Input label="Username" value={username} onChange={(e) => setUsername(e.target.value)} />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <div className="text-sm text-red-400">{error}</div>}
          <Button type="submit" loading={loading}>
            Sign In
          </Button>
          <div className="text-center text-sm text-white/60 mt-4">
            Don't have an account?{" "}
            <Link to="/register" className="text-accent hover:text-accent">
              Sign up
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};