"use client";
import { useState } from "react";
import { backendApi } from "../../lib/backend-api";

export default function ClassManager() {
  const [id, setId] = useState("demo3");
  const [joinCode, setJoinCode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function createClass() {
    setBusy(true); setMessage("");
    try {
      const result = await backendApi<{ class_id: string; join_code: string }>(
        `/api/classes?class_id=${encodeURIComponent(id.trim())}`,
        { method: "POST" },
      );
      setJoinCode(result.join_code);
      setMessage(`Class ${result.class_id} is ready. Share the join code with test students.`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Class setup failed.");
    } finally { setBusy(false); }
  }

  return <section className="panel">
    <h2>Class setup</h2>
    <p>Create the class before generating a test. Students need a join code.</p>
    <label className="field"><span>Class ID</span>
      <input value={id} onChange={e => setId(e.target.value)} maxLength={64}/>
    </label>
    <button type="button" className="button primary" onClick={createClass} disabled={busy || !id.trim()}>
      {busy ? "Working..." : "Create / Get join code"}
    </button>
    {joinCode && <p><strong>Student join code:</strong> <code>{joinCode}</code></p>}
    {message && <p role="status">{message}</p>}
  </section>;
}
