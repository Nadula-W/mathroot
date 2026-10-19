
import type { ReactNode } from "react";
import { redirect } from "next/navigation";
import { createClient } from "../../lib/supabase/server";
import AccountHeader from "./AccountHeader";

type Area = "student" | "teacher";

export default async function ProtectedArea({
  children,
  area,
}: {
  children: ReactNode;
  area: Area;
}) {
  const supabase = await createClient();

  // Check the authenticated user on the server.
  const {
    data: { user },
    error: authError,
  } = await supabase.auth.getUser();

  if (authError || !user) {
    redirect("/login");
  }

  // Read their approved role and name.
  const { data: profile, error: profileError } =
    await supabase
      .from("profiles")
      .select("full_name, role, requested_role")
      .eq("id", user.id)
      .single();

  if (profileError || !profile) {
    redirect("/login?error=profile");
  }

  // Unapproved teacher applicants cannot use either area.
  if (
    profile.role !== "teacher" &&
    profile.requested_role === "teacher"
  ) {
    redirect("/pending-teacher");
  }

  // Approved teachers should use the teacher workspace.
  if (profile.role === "teacher" && area === "student") {
    redirect("/teacher");
  }

  // Students cannot access the teacher dashboard.
  if (area === "teacher" && profile.role !== "teacher") {
    redirect("/student");
  }

  const name =
    profile.full_name?.trim() ||
    user.email?.split("@")[0] ||
    "MathRoot User";

  return (
    <>
      <AccountHeader
        name={name}
        role={area}
      />

      {children}
    </>
  );
}
