"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";



import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";

type AccountType = "student" | "teacher";

export default function RegisterPage() {
  const { t, errorText, validateInput, clearValidation } = useLanguage();
  const router = useRouter();
  const supabase = createClient();

  const [role, setRole] = useState<AccountType>("student");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function register(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!name.trim()) {
      setError("Enter your full name.");
      return;
    }

    if (password.length < 8) {
      setError("Password must contain at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      const { data, error: authError } =
        await supabase.auth.signUp({
          email: email.trim(),
          password,
          options: {
            data: {
              full_name: name.trim(),
              requested_role: role,
            },
          },
        });

      if (authError) throw authError;

      if (data.session) {
        router.replace(
          role === "teacher"
            ? "/pending-teacher"
            : "/student"
        );
        router.refresh();
        return;
      }

      setSuccess(
        "Registration submitted. Check your email " +
        "for a confirmation link, then log in."
      );

    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Registration failed."
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
        <div className="eyebrow">{t("ACCOUNT REGISTRATION")}</div>
        <h1>{t("Create Your Account")}</h1>
        <p>{t("Join MathRoot AI for Sri Lankan O/L Mathematics.")}</p>
      </section>

      <section className="panel narrow">
        <form onSubmit={register} onInvalid={validateInput} onInput={clearValidation}>
          <label className="field">
            <span>{t("Account Type")}</span>
            <select
              value={role}
              onChange={(e) =>
                setRole(e.target.value as AccountType)
              }
            >
              <option value="student">{t("Student")}</option>
              <option value="teacher">{t("Teacher")}</option>
            </select>
          </label>

          <label className="field">
            <span>{t("Full Name")}</span>
            <input
              required
              maxLength={100}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder={t("Enter your full name")}
            />
          </label>

          <label className="field">
            <span>{t("Email Address")}</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
            />
          </label>

          <label className="field">
            <span>{t("Password")}</span>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          <label className="field">
            <span>{t("Confirm Password")}</span>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
            />
          </label>

          {role === "teacher" && (
            <p className="helper">
              {t("Teacher accounts require administrator approval before accessing class results.")}
            </p>
          )}

          {error && (
            <div className="alert" role="alert">
              {errorText(error)}
            </div>
          )}

          {success && (
            <div className="alert soft" role="status">
              {t(success)}
            </div>
          )}

          <button
            type="submit"
            className="button primary full"
            disabled={loading}
          >
            {t(loading ? "Creating account..." : "Register")}
          </button>
        </form>

        <p className="helper">
          {t("Already have an account?")}{" "}
          <Link href="/login">{t("Log In")}</Link>
        </p>
      </section>
    </main>
  );
}
