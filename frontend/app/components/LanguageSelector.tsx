"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";

export default function LanguageSelector() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <label style={{ display: "inline-flex", alignItems: "center", gap: 8, fontSize: 14 }}>
      {t("Language")}
      <select
        aria-label="Language / භාෂාව"
        value={language}
        onChange={event => setLanguage(event.target.value === "si" ? "si" : "en")}
        style={{ padding: "6px 10px", borderRadius: 8, border: "1px solid #e0e6df", background: "white", font: "inherit" }}
      >
        <option value="en">English</option>
        <option value="si">සිංහල</option>
      </select>
    </label>
  );
}
