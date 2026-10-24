"use client";

import { useEffect, useState } from "react";

export default function LanguageSelector() {
  const [language, setLanguage] = useState("en");

  useEffect(() => {
    try {
      if (localStorage.getItem("mathroot.language") === "si") setLanguage("si");
    } catch { /* The selector still works when browser storage is disabled. */ }
  }, []);

  function changeLanguage(value: string) {
    setLanguage(value);
    try { localStorage.setItem("mathroot.language", value); } catch { /* Optional persistence. */ }
  }

  return (
    <label style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 14 }}>
      Language / භාෂාව
      <select
        aria-label="Language / භාෂාව"
        value={language}
        onChange={event => changeLanguage(event.target.value)}
        style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #e0e6df", background: "white", font: "inherit" }}
      >
        <option value="en">English</option>
        <option value="si">සිංහල</option>
      </select>
    </label>
  );
}
