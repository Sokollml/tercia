"""Minimal RU/EN localisation. No external dependency."""

from __future__ import annotations

from typing import Dict

DEFAULT_LANG = "ru"
SUPPORTED = ("ru", "en")

TEXTS: Dict[str, Dict[str, str]] = {
    "ru": {
        "start_hello": "Привет! Это бот розыгрышей. Нажмите «Участвую», чтобы войти в розыгрыш.",
        "start_joined": "Готово! Вы участвуете в розыгрыше «{prize}». 🎁",
        "start_no_giveaway": "Активный розыгрыш не найден.",
        "btn_participate": "🎉 Участвую",
        "btn_my_ticket": "🔗 Моя реф-ссылка",
        "already_joined": "Вы уже участвуете в этом розыгрыше.",
        "join_ok": "Вы в игре! Ваши шансы: {tickets}. Приглашайте друзей за доп. шансы.",
        "need_subscription": "Чтобы участвовать, подпишитесь на {channel} и нажмите «Участвую» снова.",
        "giveaway_ended": "Этот розыгрыш уже завершён.",
        "referral_credited": "+1 приглашённый! Ваши шансы выросли.",
        "your_ref_link": "Ваша персональная ссылка для приглашений:\n{link}\n\nПриглашено друзей: {refs}. Ваши шансы: {tickets}.",
        "admin_only": "Команда доступна только администраторам.",
        "new_giveaway_prompt": "Отправьте данные розыгрыша одной строкой:\n<приз> | <кол-во победителей> | <часов до конца> | <@канал или ->",
        "new_giveaway_bad": "Не удалось разобрать. Формат:\n<приз> | <победителей> | <часов> | <@канал|->",
        "giveaway_created": "Розыгрыш создан! ID={gid}. Пост опубликован в чат.",
        "announce": "🎁 <b>Розыгрыш: {prize}</b>\n\n{description}\n\nПобедителей: {winners}\nЗавершение: {ends}\n\nЖмите «Участвую»!",
        "stats": "📊 Розыгрыш #{gid} «{prize}»\nСтатус: {status}\nУчастников: {parts}\nВсего рефералов: {refs}\nЗавершение: {ends}\nSeed: <code>{seed}</code>",
        "no_active": "Активных розыгрышей нет.",
        "winners_announce": "🏆 <b>Итоги розыгрыша «{prize}»</b>\n\nПобедители:\n{winners}\n\nПроверяемый seed: <code>{seed}</code>\nУчастников: {parts}",
        "winners_none": "😔 В розыгрыше «{prize}» не было участников.",
        "list_header": "Участники розыгрыша #{gid} ({count}):",
        "rate_limited": "Слишком часто. Подождите секунду.",
        "error_generic": "Упс, что-то пошло не так. Попробуйте позже.",
        "lang_set": "Язык переключён на русский.",
    },
    "en": {
        "start_hello": "Hi! This is a giveaway bot. Tap “Participate” to enter.",
        "start_joined": "Done! You are in the giveaway “{prize}”. 🎁",
        "start_no_giveaway": "No active giveaway found.",
        "btn_participate": "🎉 Participate",
        "btn_my_ticket": "🔗 My referral link",
        "already_joined": "You are already in this giveaway.",
        "join_ok": "You're in! Your chances: {tickets}. Invite friends for more.",
        "need_subscription": "To join, subscribe to {channel} and tap “Participate” again.",
        "giveaway_ended": "This giveaway has already finished.",
        "referral_credited": "+1 invited friend! Your chances went up.",
        "your_ref_link": "Your personal invite link:\n{link}\n\nFriends invited: {refs}. Your chances: {tickets}.",
        "admin_only": "This command is for administrators only.",
        "new_giveaway_prompt": "Send giveaway data in one line:\n<prize> | <winners> | <hours to end> | <@channel or ->",
        "new_giveaway_bad": "Could not parse. Format:\n<prize> | <winners> | <hours> | <@channel|->",
        "giveaway_created": "Giveaway created! ID={gid}. Post published to the chat.",
        "announce": "🎁 <b>Giveaway: {prize}</b>\n\n{description}\n\nWinners: {winners}\nEnds: {ends}\n\nTap “Participate”!",
        "stats": "📊 Giveaway #{gid} “{prize}”\nStatus: {status}\nParticipants: {parts}\nTotal referrals: {refs}\nEnds: {ends}\nSeed: <code>{seed}</code>",
        "no_active": "No active giveaways.",
        "winners_announce": "🏆 <b>Giveaway “{prize}” results</b>\n\nWinners:\n{winners}\n\nVerifiable seed: <code>{seed}</code>\nParticipants: {parts}",
        "winners_none": "😔 The giveaway “{prize}” had no participants.",
        "list_header": "Participants of giveaway #{gid} ({count}):",
        "rate_limited": "Too fast. Please wait a second.",
        "error_generic": "Oops, something went wrong. Try again later.",
        "lang_set": "Language switched to English.",
    },
}


def normalize_lang(code: str) -> str:
    if not code:
        return DEFAULT_LANG
    code = code.lower().split("-")[0]
    return code if code in SUPPORTED else DEFAULT_LANG


def t(lang: str, key: str, **kwargs) -> str:
    lang = normalize_lang(lang)
    template = TEXTS.get(lang, TEXTS[DEFAULT_LANG]).get(key)
    if template is None:
        template = TEXTS[DEFAULT_LANG].get(key, key)
    try:
        return template.format(**kwargs) if kwargs else template
    except (KeyError, IndexError):
        return template
