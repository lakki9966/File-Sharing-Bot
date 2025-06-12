# utils/expiry.py

import asyncio

async def start_expiry_timer(bot, chat_id: int, msg_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await bot.delete_messages(chat_id, msg_id)
    except:
        pass
