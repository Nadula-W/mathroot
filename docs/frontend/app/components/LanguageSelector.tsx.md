# LanguageSelector.tsx — code explained

**Source:** [frontend/app/components/LanguageSelector.tsx](../../../../frontend/app/components/LanguageSelector.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** The existing selector now consumes shared language state. Its English and Sinhala options update the same global provider used by every translated page. Storage and document-language handling live in the provider.

Read the actual source blocks in order. Explanations immediately below each block describe its job and connections.


**Bilingual update:** The existing selector now consumes shared language state. Its English and Sinhala options update the same global provider used by every translated page. Storage and document-language handling live in the provider.

## Lines 1–3: Code section

```tsx
"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";

```

**Explanation:**

- The existing selector now consumes shared language state. Its English and Sinhala options update the same global provider used by every translated page. Storage and document-language handling live in the provider.

## Lines 4–21: LanguageSelector

```tsx
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
```

**Explanation:**

- The existing selector now consumes shared language state. Its English and Sinhala options update the same global provider used by every translated page. Storage and document-language handling live in the provider.

## How to explain this file in the viva

The existing selector now consumes shared language state. Its English and Sinhala options update the same global provider used by every translated page. Storage and document-language handling live in the provider.
