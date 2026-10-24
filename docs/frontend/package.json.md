# package.json — code explained

**Source:** [frontend/package.json](../../frontend/package.json) · [All frontend explanations](SOURCE_INDEX.md)

**What and how:** Defines npm commands and dependencies. scripts runs dev/build/start/typecheck; dependencies are runtime packages and devDependencies provide compiler/type tools.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–24: Code section

```json
{
  "name": "mathroot-frontend",
  "private": true,
  "version": "0.2.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "typecheck": "tsc --noEmit"
  },
  "dependencies": {
    "@supabase/ssr": "^0.12.7",
    "@supabase/supabase-js": "^2.118.0",
    "next": "16.4.2",
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  },
  "devDependencies": {
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "typescript": "^5.5.0"
  }
}
```

**Explanation:**

- Maps npm command names to executable commands.
- Packages needed by the running frontend.
- Compiler and type tooling for development.

## How to explain this file in the viva

“Defines npm commands and dependencies. scripts runs dev/build/start/typecheck; dependencies are runtime packages and devDependencies provide compiler/type tools.”
