
import type { ReactNode } from "react";
import ProtectedArea from "../components/ProtectedArea";

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
