# utils/cleanup.py

import asyncio

# User message expire avvali
async def start_expiry_timer(bot, chat_id, message_id, delay):
    await asyncio.sleep(delay)
    try:
        await bot.delete_messages(chat_id, message_id)
    except:
        pass

# Bot start ayyaka cleanup job (future use if needed)
async def start_cleanup_job(bot):
    print("Cleanup job started")
    # Future: background loops or file cleanup logic
