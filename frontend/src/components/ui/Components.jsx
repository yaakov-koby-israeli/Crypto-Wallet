export const Logo = () => (
  <div className="text-xl font-semibold tracking-[0.35em] uppercase">NEXUS</div>
);

export const ThemeToggle = ({ theme, onToggle }) => {
  return (
    <button
        onClick={onToggle}
        className="relative flex items-center rounded-full border border-white/10 dark:border-white/10 bg-white/10 dark:bg-white/5 px-2 py-1 text-xs font-medium transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent"
      >
        <span
          className={`absolute inset-y-1 w-1/2 rounded-full bg-white shadow-sm transition ${
            theme === "dark" ? "left-1" : "left-1/2"
          }`}
        />
        <span className="relative w-1/2 text-center text-[11px]">Dark</span>
        <span className="relative w-1/2 text-center text-[11px]">Light</span>
      </button>
  );
};

export const Button = ({ children, loading, variant = "primary", ...props }) => {
  const base =
    "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold transition shadow-soft focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent disabled:opacity-60 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-accent text-white hover:bg-blue-500",
    ghost:
      "bg-transparent text-white border border-white/15 hover:border-white/30",
  };
  return (
    <button className={`${base} ${variants[variant]}`} disabled={loading} {...props}>
      {loading ? (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/60 border-t-transparent" />
      ) : (
        children
      )}
    </button>
  );
};

export const Input = ({
  label,
  type = "text",
  value,
  onChange,
  placeholder,
  ...props
}) => (
  <label className="block space-y-1">
    <div className="text-xs uppercase tracking-wide text-white/60 dark:text-white/60">
      {label}
    </div>
    <input
      type={type}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="w-full rounded-lg border border-white/10 bg-white/5 px-3 py-2 text-sm text-white placeholder:text-white/30 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
      {...props}
    />
  </label>
);
