import asyncio

from formfusion.domain.errors import SessionNotFound
from formfusion.domain.models import SessionRecord


class MemorySessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}
        self._lock = asyncio.Lock()

    async def create(self, session: SessionRecord) -> None:
        async with self._lock:
            self._sessions[session.session_id] = session

    async def get(self, session_id: str) -> SessionRecord:
        async with self._lock:
            session = self._sessions.get(session_id)
            if session is None:
                raise SessionNotFound(f"session {session_id} was not found")
            return session

    async def delete(self, session_id: str) -> None:
        async with self._lock:
            if self._sessions.pop(session_id, None) is None:
                raise SessionNotFound(f"session {session_id} was not found")

    async def purge_expired(self) -> int:
        async with self._lock:
            expired = [
                session_id for session_id, session in self._sessions.items() if session.expired
            ]
            for session_id in expired:
                del self._sessions[session_id]
            return len(expired)
