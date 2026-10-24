# client.ts — code explained

**Source:** [frontend/lib/supabase/client.ts](../../../../frontend/lib/supabase/client.ts) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Creates the public browser Supabase client used by login, registration, logout and backendApi. The backend secret key must never be used here.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–2: Code section

```typescript
import { createBrowserClient } from "@supabase/ssr";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 4–9: createClient

```typescript
export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!
  );
}
```

**Explanation:**

- `createClient()`: Creates either the browser or cookie-aware server Supabase client, according to this file's location.
- These are public project settings. The backend secret key must never be placed in frontend environment values.

## How to explain this file in the viva

“Creates the public browser Supabase client used by login, registration, logout and backendApi. The backend secret key must never be used here.”
