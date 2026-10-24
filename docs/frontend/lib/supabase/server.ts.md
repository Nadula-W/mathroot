# server.ts — code explained

**Source:** [frontend/lib/supabase/server.ts](../../../../frontend/lib/supabase/server.ts) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Creates the cookie-aware Supabase client used by server components such as ProtectedArea. proxy.ts handles refresh when a rendering context cannot write cookies.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–3: Code section

```typescript
import { createServerClient } from "@supabase/ssr";
import { cookies } from "next/headers";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 5–15: createClient

```typescript
export async function createClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
```

**Explanation:**

- `createClient()`: Creates either the browser or cookie-aware server Supabase client, according to this file's location.
- These are public project settings. The backend secret key must never be placed in frontend environment values.
- The cookie adapter reads request cookies; setAll saves refreshed cookies where the server context allows it.

## Lines 17–32: Code section

```typescript
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(
              ({ name, value, options }) => {
                cookieStore.set(name, value, options);
              }
            );
          } catch {
            // Server Components cannot always set cookies.
            // Our proxy refreshes authentication sessions.
          }
        },
      },
    }
  );
}
```

**Explanation:**

- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.

## How to explain this file in the viva

“Creates the cookie-aware Supabase client used by server components such as ProtectedArea. proxy.ts handles refresh when a rendering context cannot write cookies.”
