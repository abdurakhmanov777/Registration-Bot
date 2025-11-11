"""
Модуль обработки сообщений и взаимодействия с пользователем.

Содержит функции для формирования сообщений, вывода данных
пользователя и отправки кода участника с изображением.
"""

import re
from io import BytesIO
from typing import Any, Dict, Optional, Tuple, Union

from aiogram.enums import ChatAction
from aiogram.types import (BufferedInputFile, CallbackQuery,
                           InlineKeyboardMarkup, Message)
from aiogram.types.inaccessible_message import InaccessibleMessage

from app.services.generator import generate_text_image
from app.services.keyboards import keyboards as kb
# from app.services.requests import user_action_wrapper
from app.utils.morphology import inflect_text


async def create_msg(
    loc: Any,
    state: Union[str, int],
    tg_id: int,
    bot_id: int,
    input_data: Optional[Union[str, bool]] = False,
    select: Optional[Union[Any, str, bool]] = False
) -> Tuple[str, Any]:
    """
    Формирует сообщение для пользователя в зависимости от типа состояния.

    Args:
        loc (Any): Локализация и шаблоны сообщений.
        state (Union[str, int]): Текущее состояние пользователя.
        tg_id (int): Telegram ID пользователя.
        bot_id (int): ID бота.
        input_data (Optional[str]): Данные, введённые пользователем.
        select (Optional[Tuple[Any, str]]): Выбранное значение и поле.

    Returns:
        Tuple[str, Any]: Текст сообщения и клавиатура для ответа.
    """
    current: Any
    msg_type: Any
    text: Any
    text_msg: str
    keyboard: InlineKeyboardMarkup
    current = getattr(loc, state)
    msg_type, text = current.type, current.text

    if msg_type == 'select':
        text_msg = f'{loc.template.select[0]}{text}{loc.template.select[1]}'
        keyboard = await kb.multi_select(current.keyboard)

    elif msg_type == 'input':
        user_input: str | Any = input_data or await user_action_wrapper(
            tg_id=tg_id,
            action='check',
            field=text
        )

        if input_data and not re.fullmatch(current.pattern, input_data):
            err_prefix: Any
            err_suffix: Any
            err_prefix, err_suffix = loc.template.input.error
            return f'{err_prefix}{current.format}{err_suffix}', kb.multi_back

        if user_input:
            if input_data:
                await user_action_wrapper(
                    tg_id=tg_id,
                    action='update',
                    field=text,
                    value=input_data
                )

            saved = loc.template.input.saved
            text_msg = (
                f'{saved[0]}{text}{saved[1]}{user_input}{saved[2]}'
            )
            keyboard = await kb.multi_next(current.keyboard)
        else:
            start = loc.template.input.start
            formatted_text = await inflect_text(text, 'винительный', False)
            text_msg = (
                f'{start[0]}{formatted_text}{start[1]}'
                f'{current.format}{start[2]}'
            )
            keyboard = kb.multi_back
    else:
        text_msg = text
        keyboard = await kb.multi_text(current.keyboard)

    if select:
        await user_action_wrapper(
            tg_id=tg_id,
            action='update',
            field=getattr(loc, select[1]).text,
            value=select[0]
        )

    return text_msg, keyboard


async def data_output(
    tg_id: int,
    bot_id: int,
    loc: Any
) -> Tuple[str, Any]:
    """
    Формирует сообщение с проверкой введённых пользователем данных.

    Args:
        tg_id (int): Telegram ID пользователя.
        bot_id (int): ID бота.
        loc (Any): Локализация и шаблоны сообщений.

    Returns:
        Tuple[str, Any]: Текст сообщения и клавиатура для состояния 99.
    """
    states = await user_action_wrapper(
        tg_id=tg_id,
        action='check',
        field='state'
    )

    # Преобразуем строку в список для совместимости
    if isinstance(states, str):
        states = [states]

    exclude = {'1', '99'}
    states = [s for s in states if s not in exclude]

    result = {}
    for state in states:
        field_name = getattr(loc, state).text
        value = await user_action_wrapper(
            tg_id=tg_id,
            action='check',
            field=field_name
        )
        result[field_name] = value

    items = '\n\n'.join(f'🔹️ {key}: {value}' for key, value in result.items())
    text_msg = (
        '<b><u>Проверьте свои данные</u></b>\n\n'
        f'<blockquote>{items}</blockquote>\n\n'
        '<i>Если всё верно, отправляйте данные для завершения '
        'регистрации.</i>'
    )

    return text_msg, kb.state_99


async def data_sending(
    tg_id: int,
    bot_id: int,
    event: Union[CallbackQuery, Message]
) -> None:
    """
    Отправляет пользователю изображение с кодом участника.

    Args:
        tg_id (int): Telegram ID пользователя.
        bot_id (int): ID бота.
        event (Union[CallbackQuery, Message]): Событие Telegram.

    Returns:
        None
    """
    bot = event.bot if isinstance(event, CallbackQuery) else event.bot
    message = event.message if isinstance(event, CallbackQuery) else event

    if bot:
        await bot.send_chat_action(
            chat_id=tg_id,
            action=ChatAction.UPLOAD_PHOTO
        )

    code: Any = await user_action_wrapper(
        tg_id=tg_id,
        action='check',
        field='id'  # Заменить на реальное поле идентификатора
    )

    try:
        buffer: BytesIO = await generate_text_image(str(code))

        caption: str = (
            f'<b>Код участника: {code}</b>\n\n'
            '<i>Жди подтверждения участия, которое придёт ближе к дате '
            'мероприятия!</i>'
        )
        if message:
            msg: Message = await message.answer_photo(
                photo=BufferedInputFile(buffer.read(), filename="code.png"),
                caption=caption
            )
            if bot:
                await bot.pin_chat_message(
                    chat_id=message.chat.id,
                    message_id=msg.message_id
                )
            await user_action_wrapper(
                tg_id=tg_id,
                action='update',
                field='msg_id',
                value=msg.message_id
            )

    except BaseException:
        pass

    finally:
        try:
            if message is not None and not isinstance(
                message, InaccessibleMessage
            ):
                await message.delete()
        except BaseException:
            pass
