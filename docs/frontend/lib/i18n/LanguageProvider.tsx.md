# LanguageProvider.tsx — code explained

**Source:** [frontend/lib/i18n/LanguageProvider.tsx](../../../../frontend/lib/i18n/LanguageProvider.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** One shared React context wraps the application. Initial server/client rendering is English; an effect restores mathroot.language and another updates the document language. The existing selector changes this state without remounting pages, fetching another test or resetting an answer.

Read the actual source blocks in order. Explanations immediately below each block describe its job and connections.


**Bilingual update:** One shared React context wraps the application. Initial server/client rendering is English; an effect restores mathroot.language and another updates the document language. The existing selector changes this state without remounting pages, fetching another test or resetting an answer.

**Helpers supplied by the context:** `t` translates interface messages; `topic` translates stable topic labels; `content` selects validated response fields; `errorText` translates recognized errors; `missing` checks translation warnings. `locale` supplies `en-LK` or `si-LK`. `validateInput` reads browser validity flags and sets localized required/email/length wording; `clearValidation` clears a previous message after editing. These do not relax field validity or authentication.

## Lines 1–19: LanguageContextValue

```tsx
"use client";

import { createContext, useContext, useEffect, useState, type FormEvent, type ReactNode } from "react";
import { LANGUAGE_KEY, savedLanguage, translate, topicLabel, translatedContent, translatedError, hasMissingTranslation, inputValidationMessage, type Language, type Translatable } from "./core";

type LanguageContextValue = {
  language: Language;
  setLanguage: (value: Language) => void;
  t: (message: string, values?: Record<string, string | number>) => string;
  topic: (value: string) => string;
  content: (record: Translatable, field: string) => string;
  errorText: (value: string) => string;
  missing: (record: Translatable, fields?: string[]) => boolean;
  validateInput: (event: FormEvent<HTMLFormElement>) => void;
  clearValidation: (event: FormEvent<HTMLFormElement>) => void;
  locale: "en-LK" | "si-LK";
};
const LanguageContext = createContext<LanguageContextValue | null>(null);

```

**Explanation:**

- One shared React context wraps the application. Initial server/client rendering is English; an effect restores mathroot.language and another updates the document language. The existing selector changes this state without remounting pages, fetching another test or resetting an answer.

## Lines 20–52: LanguageProvider

```tsx
export function LanguageProvider({ children }: { children: ReactNode }) {
  // Both server rendering and the first browser render use English.
  const [language, updateLanguage] = useState<Language>("en");
  useEffect(() => {
    try { updateLanguage(savedLanguage(localStorage.getItem(LANGUAGE_KEY))); } catch { /* Storage is optional. */ }
  }, []);
  useEffect(() => { document.documentElement.lang = language; }, [language]);

  function setLanguage(value: Language) {
    updateLanguage(value);
    try { localStorage.setItem(LANGUAGE_KEY, value); } catch { /* Continue without persistence. */ }
  }

  return <LanguageContext.Provider value={{
    language, setLanguage, locale: language === "si" ? "si-LK" : "en-LK",
    t: (message, values) => translate(language, message, values),
    topic: value => topicLabel(language, value),
    content: (record, field) => translatedContent(language, record, field),
    errorText: value => translatedError(language, value),
    missing: (record, fields) => hasMissingTranslation(language, record, fields),
    validateInput: event => {
      const input = event.target as HTMLInputElement;
      if (typeof input.setCustomValidity !== "function") return;
      input.setCustomValidity("");
      input.setCustomValidity(inputValidationMessage(language, input.validity, input.minLength, input.maxLength));
    },
    clearValidation: event => {
      const input = event.target as HTMLInputElement;
      if (typeof input.setCustomValidity === "function") input.setCustomValidity("");
    },
  }}>{children}</LanguageContext.Provider>;
}

```

**Explanation:**

- Keeps a single shared preference and exposes translation/display/error helpers and the chosen locale. Browser storage is optional: blocked storage does not prevent switching within the page.

## Lines 53–58: useLanguage

```tsx
export function useLanguage(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used inside LanguageProvider");
  return context;
}

```

**Explanation:**

- Reads the shared context and fails clearly if used outside its provider.

## Lines 59–62: TranslationWarning

```tsx
export function TranslationWarning({ record, fields }: { record: Translatable; fields?: string[] }) {
  const { missing, t } = useLanguage();
  return missing(record, fields) ? <span className="helper translation-warning" role="status">{t("Some content has no verified Sinhala translation. The original English is shown.")}</span> : null;
}
```

**Explanation:**

- Displays the reviewed Sinhala fallback notice only when the current record reports relevant missing translations.

## How to explain this file in the viva

One shared React context wraps the application. Initial server/client rendering is English; an effect restores mathroot.language and another updates the document language. The existing selector changes this state without remounting pages, fetching another test or resetting an answer.
