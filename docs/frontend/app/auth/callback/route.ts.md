# route.ts — code explained

**Source:** [frontend/app/auth/callback/route.ts](../../../../../frontend/app/auth/callback/route.ts) · [All frontend explanations](../../../SOURCE_INDEX.md)

**What and how:** A server request handler, not a screen: exchanges a callback code for a Supabase session, writes cookies and redirects to login with confirmation status.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–4: Code section

```typescript
import { NextResponse } from "next/server";
import { cookies } from "next/headers";
import { createServerClient } from "@supabase/ssr";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 6–16: GET

```typescript
export async function GET(request: Request) {
  const url = new URL(request.url);
  const code = url.searchParams.get("code");

  if (!code) {
    return NextResponse.redirect(
      new URL("/login?error=confirmation", request.url)
    );
  }

  const cookieStore = await cookies();
```

**Explanation:**

- `GET()`: Exchanges the callback code for a session using server cookies and redirects with confirmation status.
- Stops this server path and sends the browser to the selected login/workspace URL.

## Lines 18–38: Code section

```typescript
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(
            ({ name, value, options }) => {
              cookieStore.set(name, value, options);
            }
          );
        },
      },
    }
  );

  const { error } =
    await supabase.auth.exchangeCodeForSession(code);
```

**Explanation:**

- Exchanges the callback code for a session and stores its cookies through the adapter.
- These are public project settings. The backend secret key must never be placed in frontend environment values.
- The cookie adapter reads request cookies; setAll saves refreshed cookies where the server context allows it.

## Lines 40–48: Code section

```typescript
  return NextResponse.redirect(
    new URL(
      error
        ? "/login?error=confirmation"
        : "/login?confirmed=1",
      request.url
    )
  );
}
```

**Explanation:**

- Stops this server path and sends the browser to the selected login/workspace URL.

## How to explain this file in the viva

“A server request handler, not a screen: exchanges a callback code for a Supabase session, writes cookies and redirects to login with confirmation status.”
