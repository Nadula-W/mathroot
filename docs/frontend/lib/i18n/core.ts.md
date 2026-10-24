# core.ts — code explained

**Source:** [frontend/lib/i18n/core.ts](../../../../frontend/lib/i18n/core.ts) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Pure helpers select saved preferences, interpolate dictionary messages, localize topic labels and known errors, and read response-only Sinhala fields. They leave the canonical record unchanged and expose missing-translation warnings.

Read the actual source blocks in order. Explanations immediately below each block describe its job and connections.


**Bilingual update:** Pure helpers select saved preferences, interpolate dictionary messages, localize topic labels and known errors, and read response-only Sinhala fields. They leave the canonical record unchanged and expose missing-translation warnings.

## Lines 1–2: Code section

```typescript
import { en } from "./en";
import { si } from "./si";
```

**Explanation:**

- Pure helpers select saved preferences, interpolate dictionary messages, localize topic labels and known errors, and read response-only Sinhala fields. They leave the canonical record unchanged and expose missing-translation warnings.

## Lines 4–8: Language

```typescript
export type Language = "en" | "si";
export type Translatable = {
  translations?: { si?: Record<string, string | undefined> };
  translation_warnings?: string[];
};
```

**Explanation:**

- Pure helpers select saved preferences, interpolate dictionary messages, localize topic labels and known errors, and read response-only Sinhala fields. They leave the canonical record unchanged and expose missing-translation warnings.

## Lines 9–13: LANGUAGE_KEY

```typescript
export const LANGUAGE_KEY = "mathroot.language";

export function savedLanguage(value: string | null): Language {
  return value === "si" ? "si" : "en";
}
```

**Explanation:**

- Pure helpers select saved preferences, interpolate dictionary messages, localize topic labels and known errors, and read response-only Sinhala fields. They leave the canonical record unchanged and expose missing-translation warnings.

## Lines 15–23: translate()

```typescript
export function translate(language: Language, message: string, values: Record<string, string | number> = {}): string {
  const template = (language === "si" ? si[message] : en[message]) ?? message;
  return template.replace(/\{(\w+)\}/g, (token, name: string) => String(values[name] ?? token));
}

const topicNames: Record<string, string> = {
  binomial: "Binomial Expressions", factorization: "Factors of Quadratic Expressions",
  equations: "Equations", algebraic_fractions: "Algebraic Fractions", indices_logs: "Indices and Logarithms",
};
```

**Explanation:**

- Selects an English/Sinhala dictionary message and replaces named interpolation values. Missing keys retain the input message instead of inventing wording.

## Lines 24–28: topicLabel()

```typescript
export function topicLabel(language: Language, value: string): string {
  return translate(language, topicNames[value] ?? value);
}

// Presentation only: never replace or mutate canonical fields, expressions, IDs, or option order.
```

**Explanation:**

- Maps stable topic IDs to translated display names while leaving their stored identifiers unchanged.

## Lines 29–32: translatedContent()

```typescript
export function translatedContent(language: Language, record: Translatable, field: string): string {
  const original = (record as Record<string, unknown>)[field];
  return (language === "si" ? record.translations?.si?.[field] : undefined) ?? (typeof original === "string" ? original : "");
}
```

**Explanation:**

- Chooses a safe Sinhala field only when available; otherwise returns canonical display text. It does not mutate the supplied record.

## Lines 34–39: hasMissingTranslation()

```typescript
export function hasMissingTranslation(language: Language, record: Translatable, fields?: string[]): boolean {
  if (language !== "si") return false;
  return Boolean(record.translation_warnings?.some(field => !fields || fields.includes(field)));
}

// Browser validation still decides whether a field is valid; only its message changes.
```

**Explanation:**

- Shows a missing-field signal only in Sinhala, optionally limited to fields used by the current view.

## Lines 40–54: inputValidationMessage()

```typescript
export function inputValidationMessage(
  language: Language,
  validity: { valueMissing?: boolean; typeMismatch?: boolean; tooShort?: boolean; tooLong?: boolean },
  minLength = -1,
  maxLength = -1,
): string {
  if (validity.valueMissing) return translate(language, "Field required");
  if (validity.typeMismatch) return translate(language, "Enter a valid email address.");
  if (validity.tooShort) return translate(language, "String should have at least {count} characters", { count: minLength });
  if (validity.tooLong) return translate(language, "String should have at most {count} characters", { count: maxLength });
  return translate(language, "Invalid input");
}

// Keep raw errors in component state so a language switch also updates an existing message.
// Unknown service text remains visible with an explicit untranslated-message label.
```

**Explanation:**

- Uses existing browser validity flags to choose reviewed required/email/length wording. Native field validity and authentication rules remain unchanged.

## Lines 55–79: translatedError()

```typescript
export function translatedError(language: Language, message: string): string {
  if (!message) return "";
  if (language === "en" || si[message]) return translate(language, message);
  const rules: [RegExp, string, string[]][] = [
    [/^Class (.+) is ready\. Share the join code with (?:test|your) students\.$/, "Class {id} is ready. Share the join code with your students.", ["id"]],
    [/^Test created: (.+)$/, "Test created: {title}", ["title"]],
    [/^Topics not ready: (.+)$/, "Topics not ready: {topics}", ["topics"]],
    [/^Not enough unique questions for (.+)\.$/, "Not enough unique questions for {topic}.", ["topic"]],
    [/^Request failed: HTTP (\d+)$/, "Request failed: HTTP {status}", ["status"]],
    [/^Backend returned HTTP (\d+): ([\s\S]*)$/, "Backend returned HTTP {status}: {detail}", ["status", "detail"]],
    [/^Input should be greater than or equal to (\d+)$/, "Input should be greater than or equal to {count}", ["count"]],
    [/^Input should be less than or equal to (\d+)$/, "Input should be less than or equal to {count}", ["count"]],
    [/^String should have at least (\d+) characters?$/, "String should have at least {count} characters", ["count"]],
    [/^String should have at most (\d+) characters?$/, "String should have at most {count} characters", ["count"]],
  ];
  for (const [pattern, template, names] of rules) {
    const match = message.match(pattern);
    if (match) {
      const values = Object.fromEntries(names.map((name, index) => [name, name === "topic" ? topicLabel(language, match[index + 1]) : name === "topics" ? match[index + 1].split(", ").map(topic => topicLabel(language, topic)).join(", ") : match[index + 1]]));
      return translate(language, template, values);
    }
  }
  if (message.includes("; ")) return message.split("; ").map(part => translatedError(language, part)).join("; ");
  return translate(language, "Untranslated error: {message}", { message });
}
```

**Explanation:**

- Translates known messages and bounded error patterns while keeping raw component state. Unrecognized external text remains visible with an explicit untranslated label.

## How to explain this file in the viva

Pure helpers select saved preferences, interpolate dictionary messages, localize topic labels and known errors, and read response-only Sinhala fields. They leave the canonical record unchanged and expose missing-translation warnings.
