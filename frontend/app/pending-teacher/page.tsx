"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";



import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";

export default function PendingTeacherPage() {
  const { t } = useLanguage();
  const router = useRouter();
  const supabase = createClient();

  async function logout() {
    await supabase.auth.signOut();
    router.replace("/login");
    router.refresh();
  }

  return (
    <main className="shell student-shell">
      <section className="panel narrow">
        <h1>{t("Teacher Approval Pending")}</h1>

        <p>
          {t("Your account has been registered successfully. An administrator must approve your teacher access before you can create Mathematics tests or view student results.")}
        </p>

        <p>
          {t("If your account has been approved,")}{" "}
          <Link href="/login">{t("log in again")}</Link>.
        </p>

        <button
          className="button primary full"
          onClick={logout}
        >
          {t("Log out")}
        </button>
      </section>
    </main>
  );
}
