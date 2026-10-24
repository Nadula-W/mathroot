"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";
import { useEffect, useState } from "react";
import { backendApi } from "../../lib/backend-api";

export default function ClassManager() {
  const { t, errorText } = useLanguage();
  const [id, setId] = useState("demo3");
  const [joinCode, setJoinCode] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [classes, setClasses] = useState<{ class_id: string; join_code: string }[]>([]);
  async function reload() {
    try { setClasses(await backendApi<{ class_id: string; join_code: string }[]>("/api/classes")); }
    catch (e) { setMessage(e instanceof Error ? e.message : "Could not load classes."); }
  }
  useEffect(() => { void reload(); }, []);

  async function createClass() {
    setBusy(true); setMessage("");
    try {
      const result = await backendApi<{ class_id: string; join_code: string }>(
        `/api/classes?class_id=${encodeURIComponent(id.trim())}`,
        { method: "POST" },
      );
      setJoinCode(result.join_code);
      await reload();
      window.dispatchEvent(new Event("assessments-changed"));
      setMessage(`Class ${result.class_id} is ready. Share the join code with your students.`);
    } catch (e) {
      setMessage(e instanceof Error ? e.message : "Class setup failed.");
    } finally { setBusy(false); }
  }

  return <section className="panel">
    <h2>{t("Class setup")}</h2>
    <p>{t("Create the class before generating a test. Students need a join code.")}</p>
    <label className="field"><span>{t("Class ID")}</span>
      <input value={id} onChange={e => setId(e.target.value)} maxLength={64}/>
    </label>
    <button type="button" className="button primary" onClick={createClass} disabled={busy || !id.trim()}>
      {t(busy ? "Working..." : "Create / Get join code")}
    </button>
    {joinCode && <p><strong>{t("Student join code:")}</strong> <code>{joinCode}</code></p>}
    {message && <p role="status">{errorText(message)}</p>}
    <h3>{t("My Classes")}</h3>
    {classes.length === 0 ? <p>{t("No classes loaded yet.")}</p> : classes.map(group => <div className="test-entry" key={group.class_id}><strong>{group.class_id}</strong><span>{t("Join code:")}<code>{group.join_code}</code></span></div>)}
  </section>;
}
