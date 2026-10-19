
import type { ReactNode } from "react";
import ProtectedArea from "../components/ProtectedArea";

export default function StudentLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <ProtectedArea area="student">
      {children}
    </ProtectedArea>
  );
}