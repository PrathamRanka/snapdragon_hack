from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from jwt import InvalidTokenError

from formfusion.config import Settings
from formfusion.contracts.common import ClientRole
from formfusion.domain.errors import Unauthorized


@dataclass(frozen=True, slots=True)
class TokenClaims:
    session_id: str
    role: ClientRole
    device_id: str | None


class TokenService:
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._algorithm = settings.jwt_algorithm
        self._ttl = timedelta(seconds=settings.token_ttl_seconds)

    def issue(self, session_id: str, role: ClientRole, device_id: str | None = None) -> str:
        now = datetime.now(UTC)
        payload: dict[str, Any] = {
            "sub": device_id or role.value,
            "sid": session_id,
            "role": role.value,
            "did": device_id,
            "iat": now,
            "exp": now + self._ttl,
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify(self, token: str) -> TokenClaims:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return TokenClaims(
                session_id=str(payload["sid"]),
                role=ClientRole(str(payload["role"])),
                device_id=str(payload["did"]) if payload.get("did") else None,
            )
        except (InvalidTokenError, KeyError, ValueError) as exc:
            raise Unauthorized("invalid or expired token") from exc
