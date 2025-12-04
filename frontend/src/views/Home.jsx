import { Link } from "react-router-dom";
import { Button, Logo } from "../components/ui/Components";

export const Home = () => {
  return (
    <div className="min-h-screen bg-surface-dark text-white flex items-center justify-center px-6 py-16">
      <div className="max-w-3xl text-center space-y-8 animate-fade-slide">
        <div className="space-y-3">
          <Logo />
          <h1 className="text-4xl md:text-5xl font-semibold">Welcome to NEXUS</h1>
          <p className="text-lg text-white/70">
            The secure, real-time blockchain wallet for managing your Ethereum assets effortlessly.
          </p>
        </div>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to="/login" className="w-full sm:w-auto">
            <Button className="w-full sm:w-auto" variant="ghost">
              Sign In
            </Button>
          </Link>
          <Link to="/register" className="w-full sm:w-auto">
            <Button className="w-full sm:w-auto">
              Create Account
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
};
