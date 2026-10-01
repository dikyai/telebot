"""Telegram polling bot that stores incoming messages in Supabase."""

from __future__ import annotations

import asyncio
import logging
import os
import sys
from typing import Any

from supabase import Client, create_client
from telegram import Update
from telegram.constants import ChatType
from telegram.ext import Application, ApplicationBuilder, ContextTypes, MessageHandler, filters


TABLE_NAME = "telegram_messages"

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("telegram_supabase_bot")


def required_environment(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Environment variable {name} is required.")
    return value


def get_content_type(message: Any) -> str:
    if message.text is not None:
        return "text"
    if message.photo:
        return "photo"
    if message.video:
        return "video"
    if message.document:
        return "document"
    if message.audio:
        return "audio"
    if message.voice:
        return "voice"
    if message.video_note:
        return "video_note"
    if message.animation:
        return "animation"
    if message.sticker:
        return "sticker"
    if message.location:
        return "location"
    if message.contact:
        return "contact"
    if message.poll:
        return "poll"
    return "other"


def save_message(client: Client, row: dict[str, Any]) -> None:
    """Upsert by Telegram update ID so redelivered updates aren't duplicated."""
    (
        client.table(TABLE_NAME)
        .upsert(
            row,
            on_conflict="telegram_update_id",
            ignore_duplicates=True,
        )
        .execute()
    )


async def handle_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    message = update.effective_message
    chat = update.effective_chat
    if message is None or chat is None:
        return

    sender = update.effective_user
    row: dict[str, Any] = {
        "telegram_update_id": update.update_id,
        "telegram_message_id": message.message_id,
        "chat_id": chat.id,
        "chat_type": chat.type,
        "from_user_id": sender.id if sender else None,
        "username": sender.username if sender else None,
        "first_name": sender.first_name if sender else None,
        "last_name": sender.last_name if sender else None,
        "content_type": get_content_type(message),
        "message_text": message.text,
        "caption": message.caption,
        "message_date": message.date.isoformat(),
    }

    client: Client = context.application.bot_data["supabase"]
    try:
        await asyncio.to_thread(save_message, client, row)
    except Exception as exc:
        # Avoid logging message contents or credentials.
        logger.error(
            "Supabase save failed for Telegram update %s (%s)",
            update.update_id,
            type(exc).__name__,
        )
        if chat.type == ChatType.PRIVATE:
            await message.reply_text(
                "Pesan belum berhasil disimpan. Coba kirim lagi beberapa saat."
            )
        return

    if chat.type == ChatType.PRIVATE:
        reply = (
            "Bot aktif. Pesanmu berhasil disimpan."
            if message.text and message.text.startswith("/start")
            else "Pesan berhasil disimpan."
        )
        await message.reply_text(reply)


def build_application() -> Application:
    token = required_environment("TELEGRAM_BOT_TOKEN")
    supabase_url = required_environment("SUPABASE_URL")
    supabase_key = required_environment("SUPABASE_SERVICE_ROLE_KEY")

    application = ApplicationBuilder().token(token).build()
    application.bot_data["supabase"] = create_client(supabase_url, supabase_key)
    application.add_handler(MessageHandler(filters.ALL, handle_message))
    return application


def main() -> None:
    try:
        application = build_application()
    except Exception as exc:
        logger.error("Bot configuration failed (%s)", type(exc).__name__)
        sys.exit(1)

    logger.info("Telegram bot is starting with long polling.")
    application.run_polling(
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=False,
    )


if __name__ == "__main__":
    main()