import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import LanguageSelector from "./components/LanguageSelector";

export const metadata: Metadata = {
  title: "MathRoot AI | O/L Mathematics",
  description: "AI-ready diagnostic mathematics assessments for Sri Lankan O/L classes",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="shell" style={{ display: "flex", justifyContent: "flex-end", paddingTop: 12 }}>
          <LanguageSelector />
        </div>
        {children}
      </body>
    </html>
  );
}
