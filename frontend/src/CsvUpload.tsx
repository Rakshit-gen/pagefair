import { useRef, useState } from "react";
import { uploadIncidentsCsv } from "./api";

type Props = {
  onImported: () => void;
};

export function CsvUpload({ onImported }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [status, setStatus] = useState<string | null>(null);

  async function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const imported = await uploadIncidentsCsv(file);
      setStatus(`Imported ${imported} rows`);
      onImported();
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "Import failed");
    } finally {
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <label className="csv-upload">
      <span>Import incidents CSV</span>
      <input ref={inputRef} type="file" accept=".csv" onChange={handleChange} />
      {status && <small>{status}</small>}
    </label>
  );
}
