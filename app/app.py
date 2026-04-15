# Модуль запуска бота

from app.bot import BOT, DP


# async def start_bot():
#     # Запуск бота в режиме polling
#
#     await BOT.b.delete_webhook(drop_pending_updates=True)
#     await DP.start_polling(BOT.b, allowed_updates=DP.resolve_used_update_types())


async def start_bot(bot):
    await bot.b.delete_webhook(drop_pending_updates=True)
    await DP.start_polling(bot.b, allowed_updates=DP.resolve_used_update_types())

if __name__ == "__main__":
    pass
