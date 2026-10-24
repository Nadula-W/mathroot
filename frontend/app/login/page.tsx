"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";



import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";

export default function LoginPage() {
  const { t, errorText, validateInput, clearValidation } = useLanguage();
  const router = useRouter();
  const supabase = createClient();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function login(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const { data, error: loginError } =
        await supabase.auth.signInWithPassword({
          email: email.trim(),
          password,
        });

      if (loginError) throw loginError;

      const { data: profile, error: profileError } =
        await supabase
          .from("profiles")
          .select("role, requested_role")
          .eq("id", data.user.id)
          .single();

      if (profileError || !profile) {
        throw new Error("Could not load account profile.");
      }

      if (profile.role === "teacher") {
        router.replace("/teacher");
      } else if (profile.requested_role === "teacher") {
        router.replace("/pending-teacher");
      } else {
        router.replace("/student");
      }

      router.refresh();

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Login failed."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="shell student-shell">
      <header className="topbar">
        <Link href="/" className="logo">
          MathRoot AI
        </Link>
      </header>

      <section className="section-head">
        <div className="eyebrow">{t("ACCOUNT LOGIN")}</div>
        <h1>{t("Welcome Back")}</h1>
        <p>{t("Log in to continue learning or teaching.")}</p>
      </section>

      <section className="panel narrow">
        <form onSubmit={login} onInvalid={validateInput} onInput={clearValidation}>
          <label className="field">
            <span>{t("Email Address")}</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

          <label className="field">
            <span>{t("Password")}</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && (
            <div className="alert" role="alert">
              {errorText(error)}
            </div>
          )}

          <button
            className="button primary full"
            type="submit"
            disabled={loading}
          >
            {t(loading ? "Logging in..." : "Log In")}
          </button>
        </form>

        <p className="helper">
          {t("Don't have an account?")}{" "}
          <Link href="/register">{t("Register")}</Link>
        </p>
      </section>
    </main>
  );
}
