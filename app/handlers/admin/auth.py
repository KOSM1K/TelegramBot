from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from app.appcontext import AppContext
from app.services.admin_service import AdminService
from app.handlers.wrappers.dm_only import dm_only

router = Router()

@router.message(Command("admin_login"))
@dm_only
async def cmd_admin_login(message: types.Message, command: CommandObject, context: AppContext):
    # Security update: delete the initial message containing the token immediately
    try:
        await message.delete()
    except Exception:
        pass

    # Use the context to instantiate service
    admin_service = AdminService(context)
    
    if not command.args:
        await message.answer("❌ Usage: /admin_login <token>")
        return

    raw_token = command.args
    session = await admin_service.login_with_token(message.from_user.id, raw_token)

    if session:
        await message.answer(f"✅ Admin login successful! Session expires at {session.expires_at.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    else:
        await message.answer("❌ Invalid or revoked token.")
