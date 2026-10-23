
import { createClient } from "./supabase/client";

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
