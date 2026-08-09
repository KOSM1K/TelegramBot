import inspect
from typing import Callable, Any, Awaitable
from aiogram.types import Message
from app.services.admin_service import AdminService

def admin_session_required(handler: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    Decorator to ensure the user has an active AdminSession in the database.
    Requires 'context' to be passed as a keyword argument by the handler.
    """
    sig = inspect.signature(handler)

    async def wrapper(message: Message, *args, **kwargs) -> Any:
        # We need context to use AdminService
        context = kwargs.get('context')
        if not context:
            raise RuntimeError("admin_session_required decorator requires 'context' argument in the handler.")

        admin_service = AdminService(context)
        is_admin = await admin_service.validate_session(message.from_user.id)

        if not is_admin:
            await message.answer("🔐 Access Denied. Please login using /admin_login <token>")
            return None

        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return await handler(message, *args, **filtered_kwargs)
    
    return wrapper
