# page.tsx — code explained

**Source:** [frontend/app/register/page.tsx](../../../../frontend/app/register/page.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Validates registration fields and calls Supabase signUp. full_name/requested_role are registration metadata. An unapproved teacher waits for administrator approval.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** This module now renders user-facing wording through the shared language helpers where needed. Language changes affect labels and validated display metadata, while existing forms, requests, selected answers and saved grades retain their canonical values.

**Form validation:** `validateInput` translates native invalid-field messages; `clearValidation` removes a stale custom message when editing. These handlers change wording only. Existing name/password checks, requested teacher role and Supabase registration/approval behaviour remain in place.

## Lines 1–10: FormEvent

```tsx
"use client";
import { useLanguage } from "../../lib/i18n/LanguageProvider";



import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";

```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 11–12: AccountType

```tsx
type AccountType = "student" | "teacher";

```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 13–26: RegisterPage

```tsx
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

```

**Explanation:**

- `role` stores the requested account type, not an approved role. The paired setter updates it and triggers rendering.
- `name` stores the full-name input. The paired setter updates it and triggers rendering.
- `email` stores the email input. The paired setter updates it and triggers rendering.
- `password` stores the password input. The paired setter updates it and triggers rendering.
- `confirmPassword` stores the password confirmation. The paired setter updates it and triggers rendering.
- `loading` stores the initial-load/form waiting flag. The paired setter updates it and triggers rendering.
- `error` stores the visible error message. The paired setter updates it and triggers rendering.
- `success` stores the registration success/instructions text. The paired setter updates it and triggers rendering.

## Lines 27–48: register

```tsx
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

```

**Explanation:**

- `register()`: Checks name/password/confirmation, calls signUp and handles immediate-session versus email-confirmation registration.
- Stops the browser's native form navigation so this async React handler can display progress/errors in place.
- Applies the local minimum password-length check before making a signup request.
- Stops registration when the two typed passwords differ.

## Lines 49–73: Code section

```tsx
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

```

**Explanation:**

- Creates the account request with full_name/requested_role metadata. Teacher approval is separate; email confirmation may delay session creation.
- Changes the workspace URL without keeping the previous page in history. API permission checks still happen in Python.

## Lines 74–91: Code section

```tsx
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
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 92–97: Code section

```tsx
      <header className="topbar">
        <Link href="/" className="logo">
          MathRoot AI
        </Link>
      </header>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 98–103: Code section

```tsx
      <section className="section-head">
        <div className="eyebrow">{t("ACCOUNT REGISTRATION")}</div>
        <h1>{t("Create Your Account")}</h1>
        <p>{t("Join MathRoot AI for Sri Lankan O/L Mathematics.")}</p>
      </section>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 104–104: Code section

```tsx
      <section className="panel narrow">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 105–105: Code section

```tsx
        <form onSubmit={register} onInvalid={validateInput} onInput={clearValidation}>
```

**Explanation:**

- Connects form submission to its handler; preventDefault avoids a full browser form reload.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 106–118: Code section

```tsx
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

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 119–129: Code section

```tsx
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

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 130–140: Code section

```tsx
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

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 141–151: Code section

```tsx
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

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 152–175: Code section

```tsx
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

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 176–181: Code section

```tsx
          {success && (
            <div className="alert soft" role="status">
              {t(success)}
            </div>
          )}

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 182–198: Code section

```tsx
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
```

**Explanation:**

- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [lib/supabase/client.ts](../../lib/supabase/client.ts.md)

## How to explain this file in the viva

“Validates registration fields and calls Supabase signUp. full_name/requested_role are registration metadata. An unapproved teacher waits for administrator approval.”
