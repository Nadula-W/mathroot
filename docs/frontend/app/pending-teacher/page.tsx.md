# page.tsx — code explained

**Source:** [frontend/app/pending-teacher/page.tsx](../../../../frontend/app/pending-teacher/page.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Displays the teacher approval waiting message and provides logout. This page does not approve an account.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–6: Code section

```tsx
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Marks a client component so browser events and React state can be used. Initial HTML may still be server-rendered.

## Lines 8–10: PendingTeacherPage

```tsx
export default function PendingTeacherPage() {
  const router = useRouter();
  const supabase = createClient();
```

**Explanation:**

- This section supplies the surrounding function/component's fixed fields, messages or structure. Closing brackets complete the earlier object/call/markup; they do not make a separate request.

## Lines 12–19: logout

```tsx
  async function logout() {
    await supabase.auth.signOut();
    router.replace("/login");
    router.refresh();
  }

  return (
    <main className="shell student-shell">
```

**Explanation:**

- `logout()`: Signs out and returns to login. The shared header handles sign-out errors and disables repeated clicks while waiting.
- Changes the workspace URL without keeping the previous page in history. API permission checks still happen in Python.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 20–33: Code section

```tsx
      <section className="panel narrow">
        <h1>Teacher Approval Pending</h1>

        <p>
          Your account has been registered successfully.
          An administrator must approve your teacher
          access before you can create Mathematics tests
          or view student results.
        </p>

        <p>
          If your account has been approved,{" "}
          <Link href="/login">log in again</Link>.
        </p>
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Lines 35–44: Code section

```tsx
        <button
          className="button primary full"
          onClick={logout}
        >
          Log Out
        </button>
      </section>
    </main>
  );
}
```

**Explanation:**

- Connects the click to the named handler. The request is made by that handler, not just by rendering the button.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [lib/supabase/client.ts](../../lib/supabase/client.ts.md)

## How to explain this file in the viva

“Displays the teacher approval waiting message and provides logout. This page does not approve an account.”
