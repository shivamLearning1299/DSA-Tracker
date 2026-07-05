import { useEffect, useState } from "react";

import { apiClient } from "../api/client";
import { Sheet } from "../api/types";

export function SheetsPage() {
  const [sheets, setSheets] = useState<Sheet[]>([]);
  const [newSheetName, setNewSheetName] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    void loadSheets();
  }, []);

  async function loadSheets() {
    setIsLoading(true);
    const { data } = await apiClient.get<Sheet[]>("/api/sheets/");
    setSheets(data);
    setIsLoading(false);
  }

  async function createSheet() {
    if (!newSheetName.trim()) return;
    await apiClient.post("/api/sheets/", { name: newSheetName });
    setNewSheetName("");
    await loadSheets();
  }

  if (isLoading) return <p className="p-6 text-slate-500">Loading…</p>;

  return (
    <div className="mx-auto max-w-4xl p-6">
      <h1 className="mb-4 text-2xl font-bold text-slate-800">Sheets</h1>

      <div className="mb-6 flex gap-2">
        <input
          value={newSheetName}
          onChange={(e) => setNewSheetName(e.target.value)}
          placeholder="New sheet name (e.g. Blind 75)"
          className="flex-1 rounded-md border border-slate-300 px-3 py-2 text-sm"
        />
        <button
          onClick={() => void createSheet()}
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-700"
        >
          Create
        </button>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {sheets.map((sheet) => (
          <div
            key={sheet.id}
            className="rounded-lg border border-slate-200 bg-white p-4"
          >
            <h2 className="font-semibold text-slate-800">{sheet.name}</h2>
            <p className="mt-1 text-sm text-slate-500">
              {sheet.sheet_problems.length} problem
              {sheet.sheet_problems.length === 1 ? "" : "s"}
            </p>
            <ul className="mt-2 space-y-1 text-sm text-slate-600">
              {sheet.sheet_problems.map((sp) => (
                <li key={sp.id}>{sp.problem.title}</li>
              ))}
            </ul>
          </div>
        ))}
        {sheets.length === 0 && (
          <p className="text-slate-400">No sheets yet. Create one above.</p>
        )}
      </div>
    </div>
  );
}
