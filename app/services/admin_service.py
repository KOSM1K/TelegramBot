import hashlib
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from app.database.models.admin_session import AdminSession
from app.database.models.admin_token import AdminToken

class AdminService:
    def __init__(self, context):
        self.context = context

    def _hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def login_with_token(self, telegram_id: int, raw_token: str):
        token_hash = self._hash_token(raw_token)
        
        async with self.context.db_session_factory() as session:
            # Find the token
            stmt = select(AdminToken).where(
                AdminToken.token_hash == token_hash,
                AdminToken.owner_id == telegram_id,
                AdminToken.is_revoked == False
            )
            result = await session.execute(stmt)
            admin_token = result.scalar_one_or_none()

            if not admin_token:
                return None

            # Create/Update AdminSession
            # We check if an active session already exists for this user, or just create a new one.
            # Requirement says "create an AdminSession". 
            # Let's check for existing sessions to avoid spamming the table, but for now, simple creation is fine.
            
            expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
            session_obj = AdminSession(
                user_id=telegram_id,
                access_level=admin_token.access_level,
                expires_at=expires_at
            )
            session.add(session_obj)
            await session.commit()
            return session_obj

    async def validate_session(self, telegram_id: int):
        async with self.context.db_session_factory() as session:
            stmt = select(AdminSession).where(
                AdminSession.user_id == telegram_id,
                AdminSession.expires_at > datetime.now(timezone.utc)
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

