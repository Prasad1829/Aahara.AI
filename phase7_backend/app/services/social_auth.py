import json
import secrets
from urllib import error, parse, request

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password
from app.config import GOOGLE_CLIENT_ID
from app.models import User

GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"


def authenticate_google(db: Session, id_token: str) -> dict:
    _require_config("GOOGLE_CLIENT_ID", GOOGLE_CLIENT_ID)

    profile = _request_json(
        GOOGLE_TOKENINFO_URL,
        params={"id_token": id_token},
        provider="Google",
    )

    audience = profile.get("aud")
    issuer = profile.get("iss")
    email = profile.get("email")
    subject = profile.get("sub")

    if audience != GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token audience does not match this app.",
        )

    if issuer not in {"accounts.google.com", "https://accounts.google.com"}:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google token issuer is invalid.",
        )

    if not email or not subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google did not return a valid user profile.",
        )

    if profile.get("email_verified") is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account email is not verified.",
        )

    user = _upsert_social_user(
        db,
        email=email,
        provider="google",
        provider_subject=subject,
        full_name=profile.get("name"),
        avatar_url=profile.get("picture"),
    )
    return _build_auth_response(user)


def _require_config(name: str, value: str) -> None:
    if value:
        return

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"{name} is not configured on the backend.",
    )


def _upsert_social_user(
    db: Session,
    *,
    email: str,
    provider: str,
    provider_subject: str,
    full_name: str | None,
    avatar_url: str | None,
) -> User:
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        user = db.query(User).filter(
            User.auth_provider == provider,
            User.provider_subject == provider_subject,
        ).first()

    if user is None:
        user = User(
            email=email,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
        )
        db.add(user)

    user.full_name = full_name
    user.avatar_url = avatar_url
    user.auth_provider = provider
    user.provider_subject = provider_subject

    db.commit()
    db.refresh(user)
    return user


def _build_auth_response(user: User) -> dict:
    access_token = create_access_token({"sub": user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "avatar_url": user.avatar_url,
            "auth_provider": user.auth_provider,
        },
    }


def _request_json(
    url: str,
    *,
    method: str = "GET",
    data: dict | None = None,
    params: dict | None = None,
    headers: dict | None = None,
    provider: str,
) -> dict:
    if params:
        url = f"{url}?{parse.urlencode(params)}"

    body = None
    request_headers = {"Accept": "application/json"}
    if headers:
        request_headers.update(headers)

    if data is not None:
        body = parse.urlencode(data).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")

    req = request.Request(url, data=body, headers=request_headers, method=method)

    try:
        with request.urlopen(req, timeout=20) as response:
            payload = response.read().decode("utf-8")
            return json.loads(payload) if payload else {}
    except error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8", errors="ignore")
        detail = _parse_provider_error(provider, raw_body, f"{provider} authentication failed.")
        raise HTTPException(status_code=exc.code, detail=detail) from exc
    except error.URLError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Unable to reach {provider}. Please try again.",
        ) from exc


def _parse_provider_error(provider: str, raw_body: str, fallback: str) -> str:
    if not raw_body:
        return fallback

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return fallback

    error_payload = payload.get("error")
    if isinstance(error_payload, dict) and error_payload.get("message"):
        return error_payload["message"]
    if isinstance(error_payload, str):
        return error_payload
    if payload.get("error_description"):
        return payload["error_description"]
    return fallback
