# proxy.ts — code explained

**Source:** [frontend/proxy.ts](../../frontend/proxy.ts) · [All frontend explanations](SOURCE_INDEX.md)

**What and how:** Refreshes/validates the session for matching student/teacher URLs and propagates updated cookies. ProtectedArea handles the role redirects.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–3: NextRequest

```typescript
import { NextResponse, type NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 5–22: proxy

```typescript
export async function proxy(request: NextRequest) {
  let response = NextResponse.next({ request });

  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },

        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) => {
            request.cookies.set(name, value);
          });

          response = NextResponse.next({ request });
```

**Explanation:**

- `proxy()`: Validates/refreshes session cookies for matching routes; role navigation is still handled by ProtectedArea.
- These are public project settings. The backend secret key must never be placed in frontend environment values.
- The cookie adapter reads request cookies; setAll saves refreshed cookies where the server context allows it.
- Line 19: Updates cookies visible to the rest of this server request so later server components see the refreshed session.

## Lines 24–45: Code section

```typescript
          cookiesToSet.forEach(
            ({ name, value, options }) => {
              response.cookies.set(name, value, options);
            }
          );
        },
      },
    }
  );

  // Validate/refresh the authentication session.
  await supabase.auth.getUser();

  return response;
}

export const config = {
  matcher: [
    "/student/:path*",
    "/teacher/:path*",
  ],
};
```

**Explanation:**

- Asks Supabase to validate identity before server-side page access.
- Line 26: Adds refreshed cookies to the response so the browser stores them for later requests.

## How to explain this file in the viva

“Refreshes/validates the session for matching student/teacher URLs and propagates updated cookies. ProtectedArea handles the role redirects.”
