# tsconfig.json — code explained

**Source:** [frontend/tsconfig.json](../../frontend/tsconfig.json) · [All frontend explanations](SOURCE_INDEX.md)

**What and how:** Configures TypeScript checking. strict strengthens checks, noEmit avoids separate output, and @/* is a frontend-root import alias.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 1–21: Code section

```json
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "react-jsx",
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts", ".next/dev/types/**/*.ts"],
  "exclude": ["node_modules"]
}
```

**Explanation:**

- Enables stronger TypeScript checks.
- Checks types without generating separate output files.
- Defines the @/ import shortcut.
- Selects files for type checking.
- Excludes folders such as node_modules from project-source checking.

## How to explain this file in the viva

“Configures TypeScript checking. strict strengthens checks, noEmit avoids separate output, and @/* is a frontend-root import alias.”
