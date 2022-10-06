from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.input_media import MediaGroup, InputMediaAudio
from bot import bot

def create_inline_keyboard(buttons: list[dict] | list[tuple]):
    try:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=key, callback_data=value)
                    for key, value in i.items()
                ]
                for i in buttons
            ]
        )
    except AttributeError:
        buttons.append(("Back to main menu.", "btmm", False))
        return InlineKeyboardMarkup(
            row_width=1,
            inline_keyboard=[
                [InlineKeyboardButton(text=i[0], callback_data=i[1])]
                if not i[2]
                else [InlineKeyboardButton(text=f"{i[0]}✅", callback_data=i[1])]
                for i in buttons
            ],
        )


def create_inline_keyboard_shares(buttons: list[dict]):
    buttons.append(("Back", "main menu.", "btmm", False))
    return InlineKeyboardMarkup(
        row_width=1,
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{i[0]} to {i[1]}", callback_data=i[2])]
            if not i[3]
            else [InlineKeyboardButton(text=f"{i[0]} to {i[1]}✅", callback_data=i[2])]
            for i in buttons
        ],
    )
