# page.tsx — code explained

**Source:** [frontend/app/login/page.tsx](../../../../frontend/app/login/page.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Signs in through Supabase, reads the approved profile role and redirects to student, teacher or pending approval. The requested role alone does not authorize teacher access.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.


**Bilingual update:** This module now renders user-facing wording through the shared language helpers where needed. Language changes affect labels and validated display metadata, while existing forms, requests, selected answers and saved grades retain their canonical values.

**Form validation:** The form's `onInvalid` handler uses the provider's `validateInput` to display reviewed required/email/length messages. `onInput` clears a previous custom message after editing. The browser and Supabase still enforce the same validation/authentication rules. Raw request errors stay in state so changing language also updates a visible error.

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

## Lines 11–20: LoginPage

```tsx
export default function LoginPage() {
  const { t, errorText, validateInput, clearValidation } = useLanguage();
  const router = useRouter();
  const supabase = createClient();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

```

**Explanation:**

- `email` stores the email input. The paired setter updates it and triggers rendering.
- `password` stores the password input. The paired setter updates it and triggers rendering.
- `loading` stores the initial-load/form waiting flag. The paired setter updates it and triggers rendering.
- `error` stores the visible error message. The paired setter updates it and triggers rendering.

## Lines 21–46: login

```tsx
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

```

**Explanation:**

- `login()`: Prevents form reload, signs in with Supabase, reads the approved profile role and redirects to the correct workspace.
- Supabase checks email/password and returns a user/session. The profile query decides the approved workspace.
- Adds equality filters to scope the database request to the intended identity/class/test.
- Stops the browser's native form navigation so this async React handler can display progress/errors in place.

## Lines 47–69: Code section

```tsx
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
```

**Explanation:**

- Changes the workspace URL without keeping the previous page in history. API permission checks still happen in Python.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.
- Uses the approved database role to identify teacher access; requesting a role during signup is not sufficient.
- Detects a teacher applicant who has not yet received approved teacher access and sends them to the waiting page.

## Lines 70–75: Code section

```tsx
      <header className="topbar">
        <Link href="/" className="logo">
          MathRoot AI
        </Link>
      </header>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 76–81: Code section

```tsx
      <section className="section-head">
        <div className="eyebrow">{t("ACCOUNT LOGIN")}</div>
        <h1>{t("Welcome Back")}</h1>
        <p>{t("Log in to continue learning or teaching.")}</p>
      </section>

```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 82–82: Code section

```tsx
      <section className="panel narrow">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 83–83: Code section

```tsx
        <form onSubmit={login} onInvalid={validateInput} onInput={clearValidation}>
```

**Explanation:**

- Connects form submission to its handler; preventDefault avoids a full browser form reload.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 84–93: Code section

```tsx
          <label className="field">
            <span>{t("Email Address")}</span>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 94–109: Code section

```tsx
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

```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 110–126: Code section

```tsx
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
```

**Explanation:**

- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [lib/supabase/client.ts](../../lib/supabase/client.ts.md)

## How to explain this file in the viva

“Signs in through Supabase, reads the approved profile role and redirects to student, teacher or pending approval. The requested role alone does not authorize teacher access.”
