"""Supabase Auth verification and server-only database access for MathRoot."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

bearer = HTTPBearer(auto_error=False)


@lru_cache
def public_client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_PUBLISHABLE_KEY"])


@lru_cache
def admin_client() -> Client:
    # Do not use this client in the browser or reveal this secret in git.
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])


def current_user(
    authorization: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict:
    if authorization is None:
        raise HTTPException(status_code=401, detail="Please log in.")
    try:
        response = public_client().auth.get_user(authorization.credentials)
        user = response.user
        if not user:
            raise HTTPException(401, "Invalid login session.")
        rows = (
            admin_client().table("profiles")
            .select("id,role,requested_role,full_name")
            .eq("id", str(user.id)).limit(1).execute().data
        ) or []
        if not rows:
            raise HTTPException(403, "User profile not found.")
        return {**rows[0], "id": str(user.id)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(401, "Login session could not be verified.") from exc


def require_teacher(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "teacher":
        raise HTTPException(403, "Approved teacher account required.")
    return user


def require_student(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "student" or user["requested_role"] == "teacher":
        raise HTTPException(403, "Student account required.")
    return user
