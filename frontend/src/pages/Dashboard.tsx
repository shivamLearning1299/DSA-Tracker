import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { apiClient } from "../api/client";
import { Stats } from "../api/types";

const STATUS_COLORS: Record<string, string> = {
  todo: "#cbd5e1",
  attempted: "#fbbf24",
  solved: "#34d399",
};

export function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);

  useEffect(() => {
    (async () => {
      const { data } = await apiClient.get<Stats>("/api/stats/");
      setStats(data);
    })();
  }, []);

  if (!stats) return <p className="p-6 text-slate-500">Loading…</p>;

  const statusData = Object.entries(stats.by_status).map(([status, count]) => ({
    status,
    count,
  }));
  const difficultyData = Object.entries(stats.by_difficulty).map(
    ([difficulty, count]) => ({ difficulty, count })
  );

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="mb-4 text-2xl font-bold text-slate-800">Dashboard</h1>

      <div className="mb-6 rounded-lg border border-slate-200 bg-white p-4">
        <p className="text-sm text-slate-500">Total solved</p>
        <p className="text-3xl font-bold text-emerald-600">
          {stats.total_solved}
        </p>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="mb-2 font-semibold text-slate-800">By Status</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={statusData}
                dataKey="count"
                nameKey="status"
                outerRadius={80}
              >
                {statusData.map((entry) => (
                  <Cell
                    key={entry.status}
                    fill={STATUS_COLORS[entry.status] ?? "#94a3b8"}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-4">
          <h2 className="mb-2 font-semibold text-slate-800">By Difficulty</h2>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={difficultyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="difficulty" />
              <YAxis allowDecimals={false} />
              <Tooltip />
              <Bar dataKey="count" fill="#0f172a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="mt-6 rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="mb-2 font-semibold text-slate-800">Top Topics Solved</h2>
        <ul className="space-y-1 text-sm text-slate-600">
          {stats.by_topic.map((t) => (
            <li key={t.problem__topics__name ?? "untagged"}>
              {t.problem__topics__name ?? "Untagged"} — {t.count}
            </li>
          ))}
          {stats.by_topic.length === 0 && (
            <li className="text-slate-400">No solved problems yet.</li>
          )}
        </ul>
      </div>
    </div>
  );
}
