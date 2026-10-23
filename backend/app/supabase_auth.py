"""Supabase Auth verification and server-only database access for MathRoot."""
import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx
from supabase import Client, ClientOptions, create_client

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

bearer = HTTPBearer(auto_error=False)


def client_options() -> ClientOptions:
    # Avoid the shared HTTP/2 stream failure seen with concurrent Windows requests.
    # HTTPX clients are thread-safe; keep connection pooling over HTTP/1.1.
    return ClientOptions(httpx_client=httpx.Client(
        http2=False,
        timeout=httpx.Timeout(30.0, connect=10.0),
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    ))


@lru_cache
def public_client() -> Client:
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_PUBLISHABLE_KEY"], options=client_options())


@lru_cache
def admin_client() -> Client:
    # Do not use this client in the browser or reveal this secret in git.
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"], options=client_options())


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
    except HTTPException:
        raise
    except httpx.TransportError as exc:
        raise HTTPException(503, "Authentication service is temporarily unavailable. Please retry.") from exc
    except Exception as exc:
        raise HTTPException(401, "Login session could not be verified. Please log in again.") from exc
    try:
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
        raise HTTPException(503, "Your profile could not be loaded. Please try again.") from exc


def require_teacher(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "teacher":
        raise HTTPException(403, "Approved teacher account required.")
    return user


def require_student(user: Annotated[dict, Depends(current_user)]) -> dict:
    if user["role"] != "student" or user["requested_role"] == "teacher":
        raise HTTPException(403, "Student account required.")
    return user
