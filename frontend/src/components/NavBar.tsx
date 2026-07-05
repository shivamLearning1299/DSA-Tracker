import { NavLink } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `px-3 py-2 rounded-md text-sm font-medium ${
    isActive ? "bg-slate-900 text-white" : "text-slate-600 hover:bg-slate-100"
  }`;

export function NavBar() {
  const { user, logout } = useAuth();

  return (
    <nav className="flex items-center justify-between border-b border-slate-200 bg-white px-6 py-3">
      <div className="flex items-center gap-2">
        <span className="mr-4 text-lg font-bold text-slate-800">DSA Tracker</span>
        <NavLink to="/dashboard" className={linkClass}>
          Dashboard
        </NavLink>
        <NavLink to="/problems" className={linkClass}>
          Problems
        </NavLink>
        <NavLink to="/sheets" className={linkClass}>
          Sheets
        </NavLink>
      </div>
      <div className="flex items-center gap-3">
        <span className="text-sm text-slate-500">{user?.email}</span>
        <button
          onClick={logout}
          className="rounded-md border border-slate-300 px-3 py-1 text-sm text-slate-600 hover:bg-slate-100"
        >
          Sign out
        </button>
      </div>
    </nav>
  );
}
