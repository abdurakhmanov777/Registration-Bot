from aiogram import types


async def keyboard_dynamic(
    data: list[list[list[str]]]
) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup(
        inline_keyboard=[
            [
                types.InlineKeyboardButton(
                    text=txt,
                    url=rest[0] if typ == 'url' and rest else None,
                    web_app=types.WebAppInfo(url=rest[0]) if typ == 'webapp' and rest else None,
                    callback_data=None if typ in ['url', 'webapp'] else typ
                )
                for txt, typ, *rest in row
            ]
            for row in data
        ]
    )
