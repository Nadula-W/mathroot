# page.tsx — code explained

**Source:** [frontend/app/register/page.tsx](../../../../frontend/app/register/page.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Validates registration fields and calls Supabase signUp. full_name/requested_role are registration metadata. An unapproved teacher waits for administrator approval.

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

## Lines 9–9: AccountType

```tsx
type AccountType = "student" | "teacher";
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 11–22: RegisterPage

```tsx
export default function RegisterPage() {
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

## Lines 24–44: register

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
- Line 25: Stops the browser's native form navigation so this async React handler can display progress/errors in place.
- Line 34: Applies the local minimum password-length check before making a signup request.
- Line 39: Stops registration when the two typed passwords differ.

## Lines 46–69: Code section

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

## Lines 71–88: Code section

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

## Lines 89–93: Code section

```tsx
      <header className="topbar">
        <Link href="/" className="logo">
          MathRoot AI
        </Link>
      </header>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 95–103: Code section

```tsx
      <section className="section-head">
        <div className="eyebrow">
          ACCOUNT REGISTRATION
        </div>
        <h1>Create Your Account</h1>
        <p>
          Join MathRoot AI for Sri Lankan O/L Mathematics.
        </p>
      </section>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 105–105: Code section

```tsx
      <section className="panel narrow">
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 106–106: Code section

```tsx
        <form onSubmit={register}>
```

**Explanation:**

- Connects form submission to its handler; preventDefault avoids a full browser form reload.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 107–118: Code section

```tsx
          <label className="field">
            <span>Account Type</span>
            <select
              value={role}
              onChange={(e) =>
                setRole(e.target.value as AccountType)
              }
            >
              <option value="student">Student</option>
              <option value="teacher">Teacher</option>
            </select>
          </label>
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 120–129: Code section

```tsx
          <label className="field">
            <span>Full Name</span>
            <input
              required
              maxLength={100}
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Enter your full name"
            />
          </label>
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 131–140: Code section

```tsx
          <label className="field">
            <span>Email Address</span>
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

## Lines 142–151: Code section

```tsx
          <label className="field">
            <span>Password</span>
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

## Lines 153–176: Code section

```tsx
          <label className="field">
            <span>Confirm Password</span>
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
              Teacher accounts require administrator
              approval before accessing class results.
            </p>
          )}

          {error && (
            <div className="alert" role="alert">
              {error}
            </div>
          )}
```

**Explanation:**

- These are controlled inputs: value comes from state and onChange stores e.target.value back into that state.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 178–182: Code section

```tsx
          {success && (
            <div className="alert soft" role="status">
              {success}
            </div>
          )}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 184–200: Code section

```tsx
          <button
            type="submit"
            className="button primary full"
            disabled={loading}
          >
            {loading ? "Creating account..." : "Register"}
          </button>
        </form>

        <p className="helper">
          Already have an account?{" "}
          <Link href="/login">Log in</Link>
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
