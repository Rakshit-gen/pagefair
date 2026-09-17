const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000/api";

export type EngineerBurden = {
  engineer_email: string;
  engineer_name: string;
  incident_count: number;
  burden_score: number;
  pct_of_team_average: number;
  flag: "overloaded" | "underloaded" | "balanced";
};

export async function fetchFairness(): Promise<EngineerBurden[]> {
  const res = await fetch(`${API_BASE}/fairness/`);
  if (!res.ok) throw new Error(`Failed to load fairness report: ${res.status}`);
  return res.json();
}

export async function uploadIncidentsCsv(file: File): Promise<number> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/import/incidents/`, { method: "POST", body: form });
  if (!res.ok) throw new Error(`Import failed: ${res.status}`);
  const data = await res.json();
  return data.imported;
}
