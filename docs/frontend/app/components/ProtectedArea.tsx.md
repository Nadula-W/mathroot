# ProtectedArea.tsx — code explained

**Source:** [frontend/app/components/ProtectedArea.tsx](../../../../frontend/app/components/ProtectedArea.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** A server component that verifies the user/profile, redirects wrong/pending roles and passes the registered name to AccountHeader. FastAPI independently checks API permissions.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–5: Code section

```tsx
import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { createClient } from "../../lib/supabase/server";
import AccountHeader from "./AccountHeader";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 7–7: Area

```tsx
type Area = "student" | "teacher";
```

**Explanation:**

- These TypeScript types specify fields. [] is a list, | null permits no value, and ? marks an optional property. These compile-time checks do not validate network JSON at runtime.

## Lines 9–34: ProtectedArea

```tsx
export default async function ProtectedArea({
  children,
  area,
}: {
  children: ReactNode;
  area: Area;
}) {
  const supabase = await createClient();

  // Check the authenticated user on the server.
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  if (authError || !user) {
    redirect("/login");
  }

  // Read their approved role and name.
  const { data: profile, error: profileError } =
    await supabase
      .from("profiles")
      .select("full_name, role, requested_role")
      .eq("id", user.id)
      .single();
```

**Explanation:**

- Asks Supabase to validate identity before server-side page access.
- Stops this server path and sends the browser to the selected login/workspace URL.
- Adds equality filters to scope the database request to the intended identity/class/test.

## Lines 36–61: Code section

```tsx
  if (profileError || !profile) {
    redirect("/login?error=profile");
  }

  // Unapproved teacher applicants cannot use either area.
  if (
    profile.role !== "teacher" &&
    profile.requested_role === "teacher"
  ) {
    redirect("/pending-teacher");
  }

  // Approved teachers should use the teacher workspace.
  if (profile.role === "teacher" && area === "student") {
    redirect("/teacher");
  }

  // Students cannot access the teacher dashboard.
  if (area === "teacher" && profile.role !== "teacher") {
    redirect("/student");
  }

  const name =
    profile.full_name?.trim() ||
    user.email?.split("@")[0] ||
    "MathRoot User";
```

**Explanation:**

- Stops this server path and sends the browser to the selected login/workspace URL.
- Line 43: Detects a teacher applicant who has not yet received approved teacher access and sends them to the waiting page.
- Line 49: Uses the approved database role to identify teacher access; requesting a role during signup is not sufficient.

## Lines 63–73: Code section

```tsx
  return (
    <>
      <AccountHeader
        name={name}
        role={area}
      />

      {children}
    </>
  );
}
```

**Explanation:**

- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [app/components/AccountHeader.tsx](AccountHeader.tsx.md)
- [lib/supabase/server.ts](../../lib/supabase/server.ts.md)

## How to explain this file in the viva

“A server component that verifies the user/profile, redirects wrong/pending roles and passes the registered name to AccountHeader. FastAPI independently checks API permissions.”
