# backend-api.ts — code explained

**Source:** [frontend/lib/backend-api.ts](../../../frontend/lib/backend-api.ts) · [All frontend explanations](../SOURCE_INDEX.md)

**What and how:** The common authenticated request helper: gets the browser token, builds headers, fetches /backend plus the API path and parses success/error JSON.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–2: Code section

```typescript
import { createClient } from "./supabase/client";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 4–28: backendApi

```typescript
export async function backendApi<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const supabase = createClient();

  const {
    data: { session },
    error: authError,
  } = await supabase.auth.getSession();

  if (authError || !session) {
    throw new Error("Please log in again.");
  }

  const headers = new Headers(init.headers);

  headers.set(
    "Authorization",
    `Bearer ${session.access_token}`
  );

  if (init.body != null) {
    headers.set("Content-Type", "application/json");
  }
```

**Explanation:**

- `backendApi()`: Gets the session token, creates headers, fetches JSON through the rewrite and throws readable errors for failed responses.
- Reads the browser access token. FastAPI independently verifies it before trusting the request.
- The bearer header carries the access token. Assessment identity is not a manually entered student ID.
- Preserves caller headers before adding the shared authentication/content-type headers.

## Lines 30–55: Code section

```typescript
  const response = await fetch(`/backend${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });

  const raw = await response.text();

  let data: unknown;

  try {
    data = raw ? JSON.parse(raw) : null;
  } catch {
    throw new Error(
      `Backend returned HTTP ${response.status}: ` +
      raw.slice(0, 200)
    );
  }

  if (!response.ok) {
    const detail =
      data &&
      typeof data === "object" &&
      "detail" in data
        ? (data as { detail?: unknown }).detail
        : null;
```

**Explanation:**

- Parses response text. Invalid JSON is caught and converted into a readable error.
- Checks failure status before accepting response data.
- try attempts the operation; catch/except handles failure. finally, where present, performs cleanup even when an error occurs.
- Line 33: Requests fresh API data rather than reusing a stored response, important for progress and newly created/deleted tests.
- Line 41: An empty HTTP body becomes null; a nonempty body is parsed as JSON inside the try/catch.

## Lines 57–67: Code section

```typescript
    throw new Error(
      typeof detail === "string"
        ? detail
        : Array.isArray(detail)
        ? detail.map((item: { msg?: string }) => item.msg || "Invalid input").join("; ")
        : `Request failed: HTTP ${response.status}`
    );
  }

  return data as T;
}
```

**Explanation:**

- map creates a visible item for each record/option. key gives React a stable identity when the list updates.
- Line 66: Returns the parsed data with the caller's TypeScript type. The cast does not validate the JSON at runtime.

## Connected files

Follow these imports to their matching code explanations:

- [lib/supabase/client.ts](supabase/client.ts.md)

## How to explain this file in the viva

“The common authenticated request helper: gets the browser token, builds headers, fetches /backend plus the API path and parses success/error JSON.”
