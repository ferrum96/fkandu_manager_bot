"""Admin and moderation command handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from telegram import Update
from telegram.constants import ChatMemberStatus, ParseMode
from telegram.ext import ContextTypes

from bot import messages as msg
from bot.database import Database

if TYPE_CHECKING:
    from bot.config import Config

logger = logging.getLogger(__name__)


def _get_db(context: ContextTypes.DEFAULT_TYPE) -> Database:
    return context.application.bot_data["db"]


def _get_config(context: ContextTypes.DEFAULT_TYPE) -> "Config":
    return context.application.bot_data["config"]


def _is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    return _get_config(context).is_admin(user.id)


async def _reply_admin_only(update: Update) -> None:
    if update.message:
        await update.message.reply_text(msg.ADMIN_ONLY)


def _format_member_line(member) -> str:
    tg = member.tg_username or member.tg_first_name or str(member.user_id)
    discord = member.discord_nick or "—"
    return (
        f"• <b>{member.game_nick}</b> — {member.real_name}\n"
        f"  TG: @{tg} | Discord: {discord} | {member.perspective}"
    )


async def cmd_members(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await _reply_admin_only(update)
        return

    members = await _get_db(context).get_all_members()
    if not members:
        if update.message:
            await update.message.reply_text(msg.NO_MEMBERS)
        return

    lines = [_format_member_line(m) for m in members]
    header = f"<b>Участники клана ({len(members)}):</b>\n\n"
    text = header + "\n".join(lines)

    if update.message:
        if len(text) > 4000:
            chunks = [text[i : i + 4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                await update.message.reply_text(chunk, parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await _reply_admin_only(update)
        return

    db = _get_db(context)
    stats = await db.get_perspective_stats()
    members = await db.get_all_members()
    blacklist = await db.get_blacklist()

    fpp = stats.get("FPP", 0)
    tpp = stats.get("TPP", 0)
    mixed = stats.get("Mixed", 0)
    total = len(members)

    text = (
        "<b>📊 Статистика клана</b>\n\n"
        f"Всего участников: <b>{total}</b>\n"
        f"FPP: <b>{fpp}</b> ({_pct(fpp, total)})\n"
        f"TPP: <b>{tpp}</b> ({_pct(tpp, total)})\n"
        f"Mixed: <b>{mixed}</b> ({_pct(mixed, total)})\n\n"
        f"В чёрном списке: <b>{len(blacklist)}</b>"
    )

    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


def _pct(part: int, total: int) -> str:
    if total == 0:
        return "0%"
    return f"{round(part / total * 100)}%"


async def cmd_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await _reply_admin_only(update)
        return

    if not context.args:
        if update.message:
            await update.message.reply_text(msg.SEARCH_USAGE)
        return

    query = " ".join(context.args)
    members = await _get_db(context).search_members(query)

    if not members:
        if update.message:
            await update.message.reply_text(f"По запросу «{query}» ничего не найдено.")
        return

    lines = [_format_member_line(m) for m in members]
    text = f"<b>Результаты поиска «{query}»:</b>\n\n" + "\n".join(lines)

    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_blacklist(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await _reply_admin_only(update)
        return

    entries = await _get_db(context).get_blacklist()
    if not entries:
        if update.message:
            await update.message.reply_text("Чёрный список пуст.")
        return

    lines = [f"• ID <code>{uid}</code> — {reason}" for uid, reason, _ in entries]
    text = f"<b>Чёрный список ({len(entries)}):</b>\n\n" + "\n".join(lines)

    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def cmd_unblacklist(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not _is_admin(update, context):
        await _reply_admin_only(update)
        return

    if not context.args:
        if update.message:
            await update.message.reply_text("Использование: /unblacklist <user_id>")
        return

    try:
        user_id = int(context.args[0])
    except ValueError:
        if update.message:
            await update.message.reply_text("User ID должен быть числом.")
        return

    removed = await _get_db(context).remove_from_blacklist(user_id)
    if update.message:
        if removed:
            await update.message.reply_text(
                f"Пользователь {user_id} удалён из чёрного списка."
            )
        else:
            await update.message.reply_text(
                f"Пользователь {user_id} не найден в чёрном списке."
            )


async def cmd_kick_non_members(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Remove channel members who are not in the clan database."""
    if not _is_admin(update, context):
        await _reply_admin_only(update)
        return

    if not update.message:
        return

    config = _get_config(context)
    db = _get_db(context)
    bot = context.bot

    clan_member_ids = await db.get_member_user_ids()
    channel_member_ids = await db.get_channel_member_ids()
    admin_ids = set(config.admin_ids)

    kicked = 0
    checked = len(channel_member_ids)
    errors = 0

    if not channel_member_ids:
        await update.message.reply_text(
            "Список участников канала пуст.\n"
            "Бот отслеживает вступления автоматически — "
            "убедитесь, что он администратор канала."
        )
        return

    await update.message.reply_text("Проверяю участников канала…")

    for user_id in channel_member_ids:
        if user_id in clan_member_ids or user_id in admin_ids:
            continue

        try:
            await bot.ban_chat_member(config.channel_id, user_id)
            await bot.unban_chat_member(config.channel_id, user_id)
            await db.add_to_blacklist(user_id, "not_in_clan_kicked")
            await db.untrack_channel_member(user_id)
            kicked += 1
        except Exception:
            logger.exception("Failed to kick user %s", user_id)
            errors += 1

    await update.message.reply_text(
        f"Готово.\n"
        f"Проверено: {checked}\n"
        f"Удалено: {kicked}\n"
        f"Ошибок: {errors}"
    )


async def cmd_help_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not _is_admin(update, context):
        await _reply_admin_only(update)
        return

    text = (
        "<b>Команды администратора:</b>\n\n"
        "/members — список участников с никами\n"
        "/stats — статистика FPP/TPP\n"
        "/search &lt;запрос&gt; — поиск по никам\n"
        "/blacklist — чёрный список\n"
        "/unblacklist &lt;user_id&gt; — снять блокировку\n"
        "/kick_non_members — удалить не-участников из канала\n"
        "/admin_help — эта справка"
    )
    if update.message:
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def on_chat_member_update(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Auto-blacklist users removed from the channel."""
    if not update.chat_member:
        return

    config = _get_config(context)
    if update.chat_member.chat.id != config.channel_id:
        return

    old_status = update.chat_member.old_chat_member.status
    new_status = update.chat_member.new_chat_member.status
    user = update.chat_member.new_chat_member.user

    if user.is_bot:
        return

    removed_statuses = {
        ChatMemberStatus.LEFT,
        ChatMemberStatus.BANNED,
        ChatMemberStatus.KICKED,
    }

    was_member = old_status in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.RESTRICTED,
        ChatMemberStatus.ADMINISTRATOR,
    )

    db = _get_db(context)

    joined_statuses = (ChatMemberStatus.MEMBER, ChatMemberStatus.RESTRICTED)
    if new_status in joined_statuses and old_status not in joined_statuses:
        await db.track_channel_member(user.id)
        return

    if was_member and new_status in removed_statuses:
        await db.untrack_channel_member(user.id)
        if config.is_admin(user.id):
            return
        if await db.is_member(user.id):
            await db.add_to_blacklist(user.id, "removed_from_channel")
            logger.info("User %s blacklisted after channel removal", user.id)
