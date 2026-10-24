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

export function useLanguage(): LanguageContextValue {
  const context = useContext(LanguageContext);
  if (!context) throw new Error("useLanguage must be used inside LanguageProvider");
  return context;
}

export function TranslationWarning({ record, fields }: { record: Translatable; fields?: string[] }) {
  const { missing, t } = useLanguage();
  return missing(record, fields) ? <span className="helper translation-warning" role="status">{t("Some content has no verified Sinhala translation. The original English is shown.")}</span> : null;
}
