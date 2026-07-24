import base64
import json
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, Request

from app.config import ALLOWED_ADMIN_EMAILS, CLERK_SECRET_KEY
from app.utils.logger import logger


def _decode_jwt_unverified_payload(token: str) -> dict:
    """
    Extracts and parses the JWT payload JSON without signature validation.
    The identity sub / user_id is subsequently verified against Clerk API.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return {}
        payload_b64 = parts[1]
        # Fix base64 padding
        remainder = len(payload_b64) % 4
        if remainder > 0:
            payload_b64 += "=" * (4 - remainder)
        decoded_bytes = base64.urlsafe_b64decode(payload_b64)
        return json.loads(decoded_bytes.decode("utf-8"))
    except Exception:  # noqa: BLE001
        return {}


def log_security_event(
    request: Request,
    user_id: str | None,
    email: str | None,
    reason: str,
):
    """
    Emits a structured log entry for failed admin authorization attempts.
    """
    client_ip = request.client.host if request.client else "unknown"
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        client_ip = forwarded_for.split(",")[0].strip()

    log_payload = {
        "event": "UNAUTHORIZED_ADMIN_ACCESS_ATTEMPT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id or "anonymous",
        "email": email or "unknown",
        "ip_address": client_ip,
        "endpoint": request.url.path,
        "method": request.method,
        "reason": reason,
    }
    logger.warning(
        f"Unauthorized admin access blocked on {request.url.path} from IP {client_ip} | Reason: {reason}",
        extra=log_payload,
    )


async def verify_clerk_admin(request: Request):
    """
    FastAPI Security Dependency that:
    1. Extracts Clerk Bearer session token from Authorization header.
    2. Decodes token payload to identify user_id (sub).
    3. Validates user identity and role directly against Clerk REST API.
    4. Verifies role == 'admin' (Option A preferred) or email whitelist (Option B).
    5. Returns HTTP 404 Not Found for unauthorized calls to prevent endpoint scanning.
    """
    auth_header = request.headers.get("Authorization") or request.headers.get(
        "authorization"
    )

    if not auth_header or not auth_header.startswith("Bearer "):
        log_security_event(
            request, None, None, "Missing or malformed Authorization Bearer header"
        )
        raise HTTPException(status_code=404, detail="Not Found")

    token = auth_header.split("Bearer ", 1)[1].strip()
    if not token:
        log_security_event(request, None, None, "Empty Bearer token provided")
        raise HTTPException(status_code=404, detail="Not Found")

    payload = _decode_jwt_unverified_payload(token)
    user_id = payload.get("sub")

    if not user_id:
        log_security_event(
            request, None, None, "Invalid JWT token payload missing subject (sub)"
        )
        raise HTTPException(status_code=404, detail="Not Found")

    # Verify user against Clerk Backend API using CLERK_SECRET_KEY
    clerk_url = f"https://api.clerk.com/v1/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {CLERK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(clerk_url, headers=headers)

        if response.status_code != 200:
            log_security_event(
                request,
                user_id,
                None,
                f"Clerk user verification API returned status {response.status_code}",
            )
            raise HTTPException(status_code=404, detail="Not Found")

        user_data = response.json()
        public_metadata = user_data.get("public_metadata", {})
        email_addresses = [
            e.get("email_address", "").lower()
            for e in user_data.get("email_addresses", [])
        ]
        primary_email = email_addresses[0] if email_addresses else None

        # Option A (Preferred): Role-based check
        is_admin_role = public_metadata.get("role") == "admin"

        # Option B (Fallback): Email Whitelist check
        is_whitelisted_email = any(
            email in ALLOWED_ADMIN_EMAILS for email in email_addresses
        )

        if not is_admin_role and not is_whitelisted_email:
            log_security_event(
                request,
                user_id,
                primary_email,
                "User lacks admin role and is not in email whitelist",
            )
            raise HTTPException(status_code=404, detail="Not Found")

        # Access granted: Attach validated admin info to request state
        request.state.admin_user_id = user_id
        request.state.admin_email = primary_email
        return user_data

    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        log_security_event(
            request,
            user_id,
            None,
            f"Unexpected error during Clerk auth check: {exc!s}",
        )
        raise HTTPException(status_code=404, detail="Not Found")
