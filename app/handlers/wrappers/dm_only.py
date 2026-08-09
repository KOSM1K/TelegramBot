import inspect
from typing import Callable, Any, Awaitable
from aiogram.types import Message

def dm_only(handler: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    """
    Decorator to ensure a handler only works in private chats (DMs).
    If used in a group/channel, it deletes the message and notifies the user.
    """
    sig = inspect.signature(handler)

    async def wrapper(message: Message, *args, **kwargs) -> Any:
        if message.chat.type != "private":
            try:
                await message.delete()
            except Exception:
                pass
            
            await message.answer("⚠️ Admin commands can only be used in private chats (DMs).")
            return None 
        
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
        return await handler(message, *args, **filtered_kwargs)
    
    return wrapper
