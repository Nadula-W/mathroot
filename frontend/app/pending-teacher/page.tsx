
"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { createClient } from "../../lib/supabase/client";

export default function PendingTeacherPage() {
  const router = useRouter();
  const supabase = createClient();

  async function logout() {
    await supabase.auth.signOut();
    router.replace("/login");
    router.refresh();
  }

  return (
    <main className="shell student-shell">
      <section className="panel narrow">
        <h1>Teacher Approval Pending</h1>

        <p>
          Your account has been registered successfully.
          An administrator must approve your teacher
          access before you can create Mathematics tests
          or view student results.
        </p>

        <p>
          If your account has been approved,{" "}
          <Link href="/login">log in again</Link>.
        </p>

        <button
          className="button primary full"
          onClick={logout}
        >
          Log Out
        </button>
      </section>
    </main>
  );
}
