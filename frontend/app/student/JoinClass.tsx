"use client";
import { useState } from "react";
import { backendApi } from "../../lib/backend-api";

export default function JoinClass() {
  const [classId, setClassId] = useState("demo3");
  const [joinCode, setJoinCode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);

  async function join() {
    setBusy(true); setMessage("");
    try {
      await backendApi("/api/classes/join", {
        method: "POST",
        body: JSON.stringify({ class_id: classId.trim(), join_code: joinCode.trim() }),
      });
      setMessage("Joined successfully. You can now load tests for this class.");
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Could not join class.");
    } finally { setBusy(false); }
  }

  return <section className="panel">
    <h2>Join your Mathematics class</h2>
    <label className="field"><span>Class ID</span>
      <input maxLength={64} value={classId} onChange={e => setClassId(e.target.value)}/>
    </label>
    <label className="field"><span>Join code from your teacher</span>
      <input value={joinCode} onChange={e => setJoinCode(e.target.value)}/>
    </label>
    <button type="button" className="button primary" disabled={busy || !classId.trim() || !joinCode.trim()} onClick={join}>
      {busy ? "Joining..." : "Join class"}
    </button>
    {message && <p role="status">{message}</p>}
  </section>;
}
