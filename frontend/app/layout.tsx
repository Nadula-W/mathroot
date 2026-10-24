import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import LanguageSelector from "./components/LanguageSelector";
import { LanguageProvider } from "../lib/i18n/LanguageProvider";

export const metadata: Metadata = {
  title: "MathRoot AI | O/L Mathematics",
  description: "AI-ready diagnostic mathematics assessments for Sri Lankan O/L classes",
};

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
