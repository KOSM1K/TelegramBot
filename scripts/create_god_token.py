# docker compose exec bot env PYTHONPATH=/app python /app/scripts/create_god_token.py

import asyncio
import hashlib
import secrets
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Import your models here - Adjust the import paths as necessary for your environment
# Since we are running this as a standalone script, we need to ensure the engine and models are initialized correctly.
# We will try to use the existing app structure if possible.

from app.appcontext import AppContext
from app.database.engine import Base
from app.database.models.admin_token import AdminToken
from app.database.models.user import User

async def create_god_token(ctx: AppContext):
    print("🚀 Starting God Token creation process...")
    
    # 1. Generate a secure random token
    raw_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    
    async with ctx.db_session_factory() as session:
        # 2. Ensure the user exists (for demonstration, we'll look for a specific telegram_id or just create one)
        # For this script to be useful, you should probably provide a TG ID.
        print("⚠️ Please enter the Telegram ID of the person who should own this God Token:")
        owner_id_str = await asyncio.get_event_loop().run_in_executor(None, input)
        try:
            owner_id = int(owner_id_str)
        except ValueError:
            print("❌ Invalid Telegram ID. Please enter a numeric ID.")
            return

        # Check if user exists
        stmt = select(User).where(User.telegram_id == owner_id)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            print(f"⚠️ User with ID {owner_id} not found. Creating a new user...")
            user = User(telegram_id=owner_id, username="god_admin", balance=0)
            session.add(user)
            await session.flush() # Ensure user is in the DB to get ID if needed

        # 3. Create the AdminToken
        # We'll use a very high access level for "God" status
        GOD_ACCESS_LEVEL = 999
        
        god_token = AdminToken(
            token_hash=token_hash,
            owner_id=owner_id,
            access_level=GOD_ACCESS_LEVEL,
            is_revoked=False
        )
        session.add(god_token)
        await session.commit()
        
        print("\n✨ God Token Created Successfully!")
        print("-" * 40)
        print(f"RAW TOKEN (SAVE THIS!): {raw_token}")
        print(f"TOKEN HASH:            {token_hash}")
        print(f"OWNER ID:              {owner_id}")
        print(f"ACCESS LEVEL:          {GOD_ACCESS_LEVEL}")
        print("-" * 40)
        print("⚠️ WARNING: This token is extremely powerful. Store it securely.")

async def main():
    # Initialize context - this assumes your AppContext can run without a full bot startup
    ctx = AppContext()
    try:
        await create_god_token(ctx)
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        await ctx.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
