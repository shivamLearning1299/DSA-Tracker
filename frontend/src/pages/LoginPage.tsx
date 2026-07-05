import { Navigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { GoogleLoginButton } from "../auth/GoogleLoginButton";

export function LoginPage() {
  const { user, isLoading } = useAuth();

  if (isLoading) return null;
  if (user) return <Navigate to="/dashboard" replace />;

  return (
    <div className="flex h-screen flex-col items-center justify-center gap-6 bg-slate-50">
      <h1 className="text-3xl font-bold text-slate-800">DSA Tracker</h1>
      <p className="text-slate-500">Sign in with Google to track your progress</p>
      <GoogleLoginButton />
    </div>
  );
}
