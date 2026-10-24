# page.tsx — code explained

**Source:** [frontend/app/login/page.tsx](../../../../frontend/app/login/page.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Signs in through Supabase, reads the approved profile role and redirects to student, teacher or pending approval. The requested role alone does not authorize teacher access.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–7: FormEvent

```tsx
"use client";

import { useState, type FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 9–16: LoginPage

```tsx
export default function LoginPage() {
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

## Lines 18–42: login

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
- Line 19: Stops the browser's native form navigation so this async React handler can display progress/errors in place.

## Lines 44–66: Code section

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
- Line 44: Uses the approved database role to identify teacher access; requesting a role during signup is not sufficient.
- Line 46: Detects a teacher applicant who has not yet received approved teacher access and sends them to the waiting page.

## Lines 67–71: Code section

```tsx
      <header className="topbar">
        <Link href="/" className="logo">
          MathRoot AI
        </Link>
      </header>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 73–77: Code section

```tsx
      <section className="section-head">
        <div className="eyebrow">ACCOUNT LOGIN</div>
        <h1>Welcome Back</h1>
        <p>Log in to continue learning or teaching.</p>
      </section>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 79–79: Code section

```tsx
      <section className="panel narrow">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 80–80: Code section

```tsx
        <form onSubmit={login}>
```

**Explanation:**

- Connects form submission to its handler; preventDefault avoids a full browser form reload.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 81–89: Code section

```tsx
          <label className="field">
            <span>Email Address</span>
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

## Lines 91–105: Code section

```tsx
          <label className="field">
            <span>Password</span>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>

          {error && (
            <div className="alert" role="alert">
              {error}
            </div>
          )}
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 107–123: Code section

```tsx
          <button
            className="button primary full"
            type="submit"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>

        <p className="helper">
          Don't have an account?{" "}
          <Link href="/register">Register</Link>
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
