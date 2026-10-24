# next.config.ts — code explained

**Source:** [frontend/next.config.ts](../../frontend/next.config.ts) · [All frontend explanations](SOURCE_INDEX.md)

**What and how:** Forwards /backend requests to FastAPI on port 8000. This rewrite connects backendApi to Python and is different from the authentication proxy.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–14: Code section

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      {
        source: "/backend/:path*",
        destination: "http://127.0.0.1:8000/:path*",
      },
    ];
  },
};

export default nextConfig;
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.
- Line 7: Matches a frontend URL beginning with /backend, keeping the remaining URL in path.
- Line 8: Forwards the matched path to the local FastAPI server, stripping the frontend-only /backend prefix.

## How to explain this file in the viva

“Forwards /backend requests to FastAPI on port 8000. This rewrite connects backendApi to Python and is different from the authentication proxy.”
