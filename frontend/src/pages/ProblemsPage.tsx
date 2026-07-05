import { useEffect, useState } from "react";

import { apiClient } from "../api/client";
import { Problem, ProblemStatus } from "../api/types";

const STATUS_OPTIONS: ProblemStatus[] = ["todo", "attempted", "solved"];

const STATUS_COLORS: Record<ProblemStatus, string> = {
  todo: "bg-slate-100 text-slate-600",
  attempted: "bg-amber-100 text-amber-700",
  solved: "bg-emerald-100 text-emerald-700",
};

export function ProblemsPage() {
  const [problems, setProblems] = useState<Problem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    void loadProblems();
  }, []);

  async function loadProblems() {
    setIsLoading(true);
    const { data } = await apiClient.get<Problem[]>("/api/problems/");
    setProblems(data);
    setIsLoading(false);
  }

  async function updateStatus(problem: Problem, status: ProblemStatus) {
    await apiClient.post(`/api/problems/${problem.id}/status/`, { status });
    setProblems((prev) =>
      prev.map((p) => (p.id === problem.id ? { ...p, status } : p))
    );
  }

  if (isLoading) return <p className="p-6 text-slate-500">Loading…</p>;

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="mb-4 text-2xl font-bold text-slate-800">Problems</h1>
      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-500">
            <tr>
              <th className="px-4 py-2">Title</th>
              <th className="px-4 py-2">Difficulty</th>
              <th className="px-4 py-2">Topics</th>
              <th className="px-4 py-2">Status</th>
            </tr>
          </thead>
          <tbody>
            {problems.map((problem) => (
              <tr key={problem.id} className="border-t border-slate-100">
                <td className="px-4 py-2">
                  <a
                    href={problem.url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-slate-800 hover:underline"
                  >
                    {problem.title}
                  </a>
                </td>
                <td className="px-4 py-2 capitalize">{problem.difficulty}</td>
                <td className="px-4 py-2">
                  {problem.topics.map((t) => t.name).join(", ")}
                </td>
                <td className="px-4 py-2">
                  <select
                    value={problem.status ?? "todo"}
                    onChange={(e) =>
                      void updateStatus(problem, e.target.value as ProblemStatus)
                    }
                    className={`rounded-md border-0 px-2 py-1 text-xs font-medium ${
                      STATUS_COLORS[problem.status ?? "todo"]
                    }`}
                  >
                    {STATUS_OPTIONS.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </td>
              </tr>
            ))}
            {problems.length === 0 && (
              <tr>
                <td className="px-4 py-6 text-center text-slate-400" colSpan={4}>
                  No problems yet. Add some via the admin panel.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
