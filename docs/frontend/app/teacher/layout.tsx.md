# layout.tsx — code explained

**Source:** [frontend/app/teacher/layout.tsx](../../../../frontend/app/teacher/layout.tsx) · [All frontend explanations](../../SOURCE_INDEX.md)

**What and how:** Wraps all teacher pages in ProtectedArea with area="teacher". Approved role checks happen before the dashboard renders.

Read the code blocks in order. Each block contains the actual source and an explanation immediately below it. Line numbers match the source snapshot used here. Closing brackets and repeated markup are explained with their surrounding block.

## Lines 2–3: Code section

```tsx
import type { ReactNode } from "react";
import ProtectedArea from "../components/ProtectedArea";
```

**Explanation:**

- Imports connect this file to the named helpers/components. Relative paths start from this file. React supplies hooks, next/link supplies client navigation, and project imports connect to the helpers/components named here.

## Lines 5–15: TeacherLayout

```tsx
export default function TeacherLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <ProtectedArea area="teacher">
      {children}
    </ProtectedArea>
  );
}
```

**Explanation:**

- Passes the route's children into the server role/session wrapper.
- JSX describes the screen. className selects CSS; {...} embeds JavaScript values/conditions. Text between tags is displayed to the user.

## Connected files

Follow these imports to their matching code explanations:

- [app/components/ProtectedArea.tsx](../components/ProtectedArea.tsx.md)

## How to explain this file in the viva

“Wraps all teacher pages in ProtectedArea with area="teacher". Approved role checks happen before the dashboard renders.”
