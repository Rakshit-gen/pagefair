import { useCallback, useEffect, useState } from "react";
import { fairnessExportUrl, fetchFairness, type EngineerBurden } from "./api";
import { CsvUpload } from "./CsvUpload";

export default function App() {
  const [report, setReport] = useState<EngineerBurden[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [windowDays, setWindowDays] = useState(90);

  const reload = useCallback(() => {
    setLoading(true);
    fetchFairness(windowDays)
      .then(setReport)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [windowDays]);

  useEffect(() => {
    reload();
  }, [reload]);

  const maxPct = Math.max(100, ...report.map((r) => r.pct_of_team_average));

  return (
    <div className="app">
      <header>
        <h1>pagefair</h1>
        <p>On-call burden weighted by severity, off-hours pages, and resolution time.</p>
        <a className="export-link" href={fairnessExportUrl(windowDays)}>
          Export report as CSV
        </a>
      </header>

      <section className="uploads">
        <CsvUpload onImported={reload} />
        <label className="csv-upload">
          <span>Window</span>
          <select value={windowDays} onChange={(e) => setWindowDays(Number(e.target.value))}>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={365}>Last 365 days</option>
          </select>
        </label>
      </section>

      {error && <p className="error">{error}</p>}

      {loading ? (
        <p className="empty">Loading fairness report…</p>
      ) : report.length === 0 && !error ? (
        <p className="empty">No incidents yet. Import a CSV above to see the report.</p>
      ) : (
        <div className="report">
          {report.map((r) => (
            <div key={r.engineer_email} className={`bar-row flag-${r.flag}`}>
              <div className="bar-label">
                <strong>{r.engineer_name}</strong>
                <span>
                  {r.incident_count} incidents · burden {r.burden_score} ·{" "}
                  {r.pct_of_team_average}% of team average
                </span>
              </div>
              <div className="bar-track">
                <div
                  className="bar-fill"
                  style={{ width: `${(r.pct_of_team_average / maxPct) * 100}%` }}
                />
              </div>
              <span className="bar-flag">{r.flag}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
