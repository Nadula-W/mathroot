# layout.tsx — code explained

**Source:** [frontend/app/layout.tsx](../../../frontend/app/layout.tsx) · [All frontend explanations](../SOURCE_INDEX.md)

**What and how:** RootLayout supplies the shared HTML/body, metadata and CSS. children is the selected page rendered inside it.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** The server root layout mounts one client LanguageProvider and the existing selector around the same page children. English initial HTML is consistent with the first client render; the provider applies a saved preference after mounting.

## Lines 1–11: metadata

```tsx
import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import LanguageSelector from "./components/LanguageSelector";
import { LanguageProvider } from "../lib/i18n/LanguageProvider";

export const metadata: Metadata = {
  title: "MathRoot AI | O/L Mathematics",
  description: "AI-ready diagnostic mathematics assessments for Sri Lankan O/L classes",
};

```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 12–25: RootLayout

```tsx
export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <LanguageProvider>
        <nav className="shell language-navigation" aria-label="Language / භාෂාව">
          <LanguageSelector />
        </nav>
        {children}
        </LanguageProvider>
      </body>
    </html>
  );
}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## How to explain this file in the viva

“RootLayout supplies the shared HTML/body, metadata and CSS. children is the selected page rendered inside it.”
