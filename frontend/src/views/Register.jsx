import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button, Input, Logo } from "../components/ui/Components";

export const Register = ({ onRegister, loading, error }) => {
  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    role: "user",
  });
  const [fieldErrors, setFieldErrors] = useState({});
  const navigate = useNavigate();

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const validate = () => {
    const errs = {};
    if (!form.username.trim()) errs.username = "Username is required";
    if (!form.email.trim()) errs.email = "Email is required";
    if (!form.first_name.trim()) errs.first_name = "First name is required";
    if (!form.last_name.trim()) errs.last_name = "Last name is required";
    if (!form.password.trim()) {
      errs.password = "Password is required";
    } else if (form.password.trim().length < 6) {
      errs.password = "Password must be at least 6 characters";
    }
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setFieldErrors({});
    const ok = await onRegister(form);
    if (ok) {
      navigate("/login");
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-dark text-white">
      <div className="w-full max-w-2xl rounded-2xl border border-white/10 bg-white/5 p-8 shadow-soft backdrop-blur animate-fade-slide">
        <div className="mb-6 flex items-center justify-between">
          <Logo />
          <div className="text-sm text-white/60">Create your account</div>
        </div>
        <form className="grid grid-cols-1 gap-4 md:grid-cols-2" onSubmit={submit} noValidate>
          <div>
            <Input label="Username" value={form.username} onChange={update("username")} />
            {fieldErrors.username && (
              <div className="mt-1 text-xs text-red-400">{fieldErrors.username}</div>
            )}
          </div>
          <div>
            <Input label="Email" type="email" value={form.email} onChange={update("email")} />
            {fieldErrors.email && (
              <div className="mt-1 text-xs text-red-400">{fieldErrors.email}</div>
            )}
          </div>
          <div>
            <Input label="First Name" value={form.first_name} onChange={update("first_name")} />
            {fieldErrors.first_name && (
              <div className="mt-1 text-xs text-red-400">{fieldErrors.first_name}</div>
            )}
          </div>
          <div>
            <Input label="Last Name" value={form.last_name} onChange={update("last_name")} />
            {fieldErrors.last_name && (
              <div className="mt-1 text-xs text-red-400">{fieldErrors.last_name}</div>
            )}
          </div>
          <div className="md:col-span-2">
            <Input
              label="Password"
              type="password"
              value={form.password}
              onChange={update("password")}
            />
            {fieldErrors.password && (
              <div className="mt-1 text-xs text-red-400">{fieldErrors.password}</div>
            )}
          </div>
          <div className="md:col-span-2">
            {error && <div className="mb-2 text-sm text-red-400">{error}</div>}
            <Button type="submit" loading={loading}>
              Register
            </Button>
            <div className="text-center text-sm text-white/60 mt-4">
              Already have an account?{" "}
              <Link to="/login" className="text-accent hover:text-accent">
                Sign in
              </Link>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};
