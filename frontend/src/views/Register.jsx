import { useState } from "react";
import { Button, Input, Logo } from "../components/ui/Components";

export const Register = ({ onRegister, loading, error }) => {
  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    password: "",
    role: "user",
    public_key: "",
  });

  const update = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    onRegister(form);
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-surface-dark text-white">
      <div className="w-full max-w-2xl rounded-2xl border border-white/10 bg-white/5 p-8 shadow-soft backdrop-blur animate-fade-slide">
        <div className="mb-6 flex items-center justify-between">
          <Logo />
          <div className="text-sm text-white/60">Create your account</div>
        </div>
        <form className="grid grid-cols-1 gap-4 md:grid-cols-2" onSubmit={submit}>
          <Input label="Username" value={form.username} onChange={update("username")} />
          <Input label="Email" type="email" value={form.email} onChange={update("email")} />
          <Input label="First Name" value={form.first_name} onChange={update("first_name")} />
          <Input label="Last Name" value={form.last_name} onChange={update("last_name")} />
          <Input
            label="Password"
            type="password"
            value={form.password}
            onChange={update("password")}
          />
          <Input
            label="Public Key"
            value={form.public_key}
            onChange={update("public_key")}
            placeholder="0x..."
          />
          <div className="md:col-span-2">
            {error && <div className="mb-2 text-sm text-red-400">{error}</div>}
            <Button type="submit" loading={loading}>
              Register
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
