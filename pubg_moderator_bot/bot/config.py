"""Configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _parse_admin_ids(raw: str) -> list[int]:
    if not raw.strip():
        return []
    return [int(x.strip()) for x in raw.split(",") if x.strip()]


@dataclass(frozen=True)
class Config:
    bot_token: str
    channel_id: int
    admin_ids: list[int] = field(default_factory=list)
    telegram_channel_link: str = ""
    discord_link: str = ""
    google_sheets_credentials_file: str = ""
    google_sheet_id: str = ""
    database_path: str = "data/bot.db"
    max_survey_attempts: int = 2

    @classmethod
    def from_env(cls) -> "Config":
        token = os.getenv("BOT_TOKEN", "")
        if not token:
            raise ValueError("BOT_TOKEN is required")

        channel_id = os.getenv("CHANNEL_ID", "")
        if not channel_id:
            raise ValueError("CHANNEL_ID is required")

        return cls(
            bot_token=token,
            channel_id=int(channel_id),
            admin_ids=_parse_admin_ids(os.getenv("ADMIN_IDS", "")),
            telegram_channel_link=os.getenv("TELEGRAM_CHANNEL_LINK", ""),
            discord_link=os.getenv("DISCORD_LINK", ""),
            google_sheets_credentials_file=os.getenv(
                "GOOGLE_SHEETS_CREDENTIALS_FILE", ""
            ),
            google_sheet_id=os.getenv("GOOGLE_SHEET_ID", ""),
            database_path=os.getenv("DATABASE_PATH", "data/bot.db"),
        )

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admin_ids
