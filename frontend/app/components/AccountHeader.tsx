"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";



import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { createClient } from "../../lib/supabase/client";

export default function AccountHeader({
  name,
  role,
}: {
  name: string;
  role: "student" | "teacher";
}) {

  const { t, errorText } = useLanguage();
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);
  const [error, setError] = useState("");

  async function logout() {
    setLoggingOut(true);
    setError("");

    const supabase = createClient();

    const { error: signOutError } =
      await supabase.auth.signOut();

    if (signOutError) {
      setError(signOutError.message);
      setLoggingOut(false);
      return;
    }

    router.replace("/login");
    router.refresh();
  }

  return (
    <header className="mr-account-header">
      <div className="mr-account-brand">
        <Link href={role === "teacher" ? "/teacher" : "/student"}>
          MathRoot AI
        </Link>
        <span className="mr-account-section">
          {role === "teacher"
            ? t("Teacher Workspace")
            : t("Student Workspace")}
        </span>
      </div>

      <div className="mr-account-right">
        <div className="mr-account-user">
          <span className="mr-account-greeting">{t("Hi, {name}", { name })}</span>
          <span className="mr-account-role">
            {t(role === "teacher" ? "Teacher" : "Student")}
          </span>
        </div>

        <button
          type="button"
          className="mr-account-logout"
          onClick={logout}
          disabled={loggingOut}
        >
          {t(loggingOut ? "Logging out..." : "Log out")}
        </button>
      </div>

      {error && (
        <p className="mr-account-error" role="alert">
          {errorText(error)}
        </p>
      )}
    </header>
  );
}
