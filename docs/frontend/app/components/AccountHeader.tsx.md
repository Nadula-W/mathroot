# AccountHeader.tsx — code explained

**Source:** [frontend/app/components/AccountHeader.tsx](../../../../frontend/app/components/AccountHeader.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Receives name/role from ProtectedArea, displays account navigation and signs out with the browser Supabase client. Failed sign-out is shown as an error.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–7: Code section

```tsx
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { createClient } from "../../lib/supabase/client";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 9–18: AccountHeader

```tsx
export default function AccountHeader({
  name,
  role,
}: {
  name: string;
  role: "student" | "teacher";
}) {
  const router = useRouter();
  const [loggingOut, setLoggingOut] = useState(false);
  const [error, setError] = useState("");
```

**Explanation:**

- `loggingOut` stores the sign-out waiting flag. The paired setter updates it and triggers rendering.
- `error` stores the visible error message. The paired setter updates it and triggers rendering.

## Lines 20–39: logout

```tsx
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
```

**Explanation:**

- `logout()`: Signs out and returns to login. The shared header handles sign-out errors and disables repeated clicks while waiting.
- Changes the workspace URL without keeping the previous page in history. API permission checks still happen in Python.

## Lines 40–60: Code section

```tsx
    <header className="mr-account-header">
      <div className="mr-account-brand">
        <Link href={role === "teacher" ? "/teacher" : "/student"}>
          MathRoot AI
        </Link>
        <span className="mr-account-section">
          {role === "teacher"
            ? "Teacher Workspace"
            : "Student Workspace"}
        </span>
      </div>

      <div className="mr-account-right">
        <div className="mr-account-user">
          <span className="mr-account-greeting">
            Hi, {name}
          </span>
          <span className="mr-account-role">
            {role === "teacher" ? "Teacher" : "Student"}
          </span>
        </div>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 62–79: Code section

```tsx
        <button
          type="button"
          className="mr-account-logout"
          onClick={logout}
          disabled={loggingOut}
        >
          {loggingOut ? "Logging out..." : "Log out"}
        </button>
      </div>

      {error && (
        <p className="mr-account-error" role="alert">
          {error}
        </p>
      )}
    </header>
  );
}
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- Guards missing inputs, busy operations or already-submitted answers in the UI; server validation remains required.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [lib/supabase/client.ts](../../lib/supabase/client.ts.md)

## How to explain this file in the viva

“Receives name/role from ProtectedArea, displays account navigation and signs out with the browser Supabase client. Failed sign-out is shown as an error.”
