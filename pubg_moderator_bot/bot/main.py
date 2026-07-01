"""Entry point for the clan moderator bot."""

import logging

from telegram.ext import (
    Application,
    ChatMemberHandler,
    CommandHandler,
)

from bot.config import Config
from bot.database import Database
from bot.google_sheets import SheetsSync
from bot.handlers.admin import (
    cmd_assign_titles,
    cmd_blacklist,
    cmd_help_admin,
    cmd_kick_non_members,
    cmd_members,
    cmd_search,
    cmd_stats,
    cmd_unblacklist,
    on_chat_member_update,
)
from bot.handlers.survey import build_survey_handler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    db: Database = application.bot_data["db"]
    await db.init()
    logger.info("Database initialized")


def main() -> None:
    config = Config.from_env()
    db = Database(config.database_path)
    sheets = SheetsSync(config)

    application = (
        Application.builder()
        .token(config.bot_token)
        .post_init(post_init)
        .build()
    )

    application.bot_data["config"] = config
    application.bot_data["db"] = db
    application.bot_data["sheets"] = sheets

    application.add_handler(build_survey_handler())

    application.add_handler(CommandHandler("members", cmd_members))
    application.add_handler(CommandHandler("stats", cmd_stats))
    application.add_handler(CommandHandler("search", cmd_search))
    application.add_handler(CommandHandler("blacklist", cmd_blacklist))
    application.add_handler(CommandHandler("unblacklist", cmd_unblacklist))
    application.add_handler(CommandHandler("kick_non_members", cmd_kick_non_members))
    application.add_handler(CommandHandler("assign_titles", cmd_assign_titles))
    application.add_handler(CommandHandler("admin_help", cmd_help_admin))

    application.add_handler(
        ChatMemberHandler(on_chat_member_update, ChatMemberHandler.CHAT_MEMBER)
    )

    logger.info("Bot starting…")
    application.run_polling(allowed_updates=["message", "callback_query", "chat_member"])


if __name__ == "__main__":
    main()
