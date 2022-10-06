from operator import mod
from bot import dispatcher, bot
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.types.message import ContentTypes
from aiogram.types.input_media import MediaGroup, InputMediaAudio
from models import TgUser, Audio, Playlist, Shared
from tortoise.exceptions import IntegrityError
from utils import create_inline_keyboard, create_inline_keyboard_shares


##### MAIN
@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "btmm", state="*"
)
async def main_munu(query: CallbackQuery, state: FSMContext):
    await state.reset_state()
    await state.reset_data()
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Any more?",
        reply_markup=create_inline_keyboard(
            [
                {"Create new": "cr", "Choose active": "ch"},
                {"Fren activities": "fr", "Delete old": "del"},
                {"Retrieve": "rt"},
            ]
        ),
    )

##### AUDIO
@dispatcher.message_handler(content_types=ContentTypes.AUDIO, state="*")
async def audio_handler(message: Message, state: FSMContext):
    await state.reset_state()
    pl = await Playlist.get_or_none(owner_id=message.from_id, active=True)
    if not pl:
        await bot.send_message(
            chat_id=message.chat.id,
            text="You should make one of your playlists active to add music there or create a fresh one. I cannot add this track to nowhere, can I?",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        return

    a = await pl.audios.filter(file_unique_id=message.audio.file_unique_id)
    if a:
        await pl.audios.remove(a[0])
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Succesfully deleted '{message.audio.title}'. What's next?",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
    else:
        audio = await Audio.get_or_create(file_unique_id=message.audio.file_unique_id)
        if audio[1]:
            audio[0].name = message.audio.title[:20]
            audio[0].file_id = message.audio.file_id
            await audio[0].save()
        await pl.audios.add(audio[0])
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Succesfully stored '{message.audio.title}'. What's next?",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )

    await message.delete()

##### START
@dispatcher.message_handler(commands=["start"], state="*")
async def start(message: Message, state: FSMContext):
    await state.reset_state()

    await bot.send_message(
        chat_id=message.chat.id,
        text="This is porte's playlist bot. It will store your playlists so you can retrieve them at any time. Feel free to give me any amount of free money: @PorteDonate.",
        reply_markup=create_inline_keyboard(
            [
                {"Create new": "cr", "Choose active": "ch"},
                {"Fren activities": "fr", "Delete old": "del"},
                {"Retrieve": "rt"},
            ]
        ),
    )

##### CREATION
@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "cr", state="*"
)
async def create(query: CallbackQuery, state: FSMContext):
    await state.set_state("creation")
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose a name for your playlist:",
        reply_markup=create_inline_keyboard([{"Back to main menu.": "btmm"}]),
    )


@dispatcher.message_handler(state="creation")
async def sdtp_creation(message: Message, state: FSMContext):
    user = await TgUser.get_or_create(id=message.from_id)
    try:
        await Playlist.create(owner=user[0], name=message.text[0:40])
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"A playlist named '{message.text[0:40]}' have succesfully been created.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
    except IntegrityError:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Try another name, not one you *have* alredy had:",
            reply_markup=create_inline_keyboard([{"Back to main menu.": "btmm"}]),
        )


@dispatcher.message_handler(state="creation")
async def sdtp_creation(message: Message, state: FSMContext):
    user = await TgUser.get_or_create(id=message.from_id)
    try:
        await Playlist.create(owner=user[0], name=message.text[0:40])
        await bot.send_message(
            chat_id=message.chat.id,
            text=f"A playlist named '{message.text[0:40]}' have succesfully been created.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
    except IntegrityError:
        await bot.send_message(
            chat_id=message.chat.id,
            text="Try another name, not one you *have* alredy had:",
            reply_markup=create_inline_keyboard({"Back to main menu.": "btmm"}),
        )

##### ACTIVATION
@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "ch", state="*"
)
async def activate(query: CallbackQuery, state: FSMContext):
    await state.set_state("activate")
    playlists = (
        await Playlist.filter(owner_id=query.message.chat.id)
        .order_by("id")
        .values_list("name", "id", "active")
    )
    if playlists.__len__() == 0:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="You cannot make active a non-existent playlist.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
        return
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose active playlist:",
        reply_markup=create_inline_keyboard(playlists),
    )


@dispatcher.callback_query_handler(state="activate")
async def activation(query: CallbackQuery, state: FSMContext):
    p_active = await Playlist.get_or_none(owner_id=query.message.chat.id, active=True)
    p_not = await Playlist.get_or_none(id=query.data)
    if p_active:
        p_active = await p_active.update_from_dict(data={"active": False})
        await p_active.save()
    if p_not:
        p_not = await p_not.update_from_dict(data={"active": True})
        await p_not.save()
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Done!",
        reply_markup=create_inline_keyboard(
            [
                {"Create new": "cr", "Choose active": "ch"},
                {"Fren activities": "fr", "Delete old": "del"},
                {"Retrieve": "rt"},
            ]
        ),
    )
    await state.reset_state()

##### DELETION
@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "del", state="*"
)
async def delete(query: CallbackQuery, state: FSMContext):
    await state.set_state("deletion")
    playlists = (
        await Playlist.filter(owner_id=query.message.chat.id)
        .order_by("id")
        .values_list("name", "id", "active")
    )
    if playlists.__len__() == 0:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="You have no playlists to delete.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
        return
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose a playlist to delete:",
        reply_markup=create_inline_keyboard(playlists),
    )


@dispatcher.callback_query_handler(state="deletion")
async def deletion(query: CallbackQuery, state: FSMContext):
    to_delete = await Playlist.get_or_none(id=query.data)
    await to_delete.delete()
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Done!",
        reply_markup=create_inline_keyboard(
            [
                {"Create new": "cr", "Choose active": "ch"},
                {"Fren activities": "fr", "Delete old": "del"},
                {"Retrieve": "rt"},
            ]
        ),
    )
    await state.reset_state()

##### RETRIEVAL
@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "rt", state="*"
)
async def retrieve(query: CallbackQuery, state: FSMContext):
    await state.set_state("retrieval")
    playlists = (
        await Playlist.filter(owner_id=query.message.chat.id)
        .order_by("id")
        .values_list("name", "id", "active")
    )
    shared = (
        await Shared.filter(shared_to=query.message.chat.id, accepted=True)
        .order_by("id")
        .values_list("playlist__name", "playlist__id", "accepted")
    )
    if (shared.__len__() + playlists.__len__()) == 0:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="You have nothing to retrieve.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
        return
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose wisely:",
        reply_markup=create_inline_keyboard(playlists + shared),
    )


@dispatcher.callback_query_handler(state="retrieval")
async def retrieval(query: CallbackQuery, state: FSMContext):
    user = await TgUser.get(id=query.message.chat.id)
    last, last_amount = user.last, user.last_amount
    for i in range(last, last + last_amount):
        await bot.delete_message(chat_id=query.message.chat.id, message_id=i)
    retrieving = await Playlist.get_or_none(id=query.data)
    ids = await retrieving.audios.all().values_list("file_id", flat=True)
    q = True
    for i in range((ids.__len__() // 10) + 1):
        a = await bot.send_media_group(
            chat_id=query.message.chat.id,
            media=[InputMediaAudio(media=k) for k in ids[i * 10 : (i + 1) * 10]],
        )
        if q:
            user.last = a[0].message_id
            q = False
    user.last_amount = ids.__len__()
    await user.save()
    await state.reset_state()

##### FRENS
@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "fr", state="*"
)
async def frens(query: CallbackQuery, state: FSMContext):
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose fren activity:",
        reply_markup=create_inline_keyboard(
            [
                {"Grant access": "ga", "Accept access": "aa"},
                {"My shares": "mys", "Back to main menu.": "btmm"},
            ]
        ),
    )


@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "ga", state="*"
)
async def grant_access(query: CallbackQuery, state: FSMContext):
    await state.set_state("grant_frens")
    playlists = (
        await Playlist.filter(owner_id=query.message.chat.id)
        .order_by("id")
        .values_list("name", "id", "active")
    )
    if playlists.__len__() == 0:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="You have nothing to share.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
        return
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose what to share:",
        reply_markup=create_inline_keyboard(playlists),
    )


@dispatcher.callback_query_handler(state="grant_frens")
async def grant_access_choise(query: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["choise"] = query.data
    await state.set_state("grant_frens_tag")
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Share with me contact of a person to share playlist with or its numerical id:",
        reply_markup=create_inline_keyboard(
            [
                {"Back to main menu.": "btmm"},
            ]
        ),
    )


@dispatcher.message_handler(
    content_types=ContentTypes.CONTACT | ContentTypes.TEXT, state="grant_frens_tag"
)
async def grant_access_tag(message: Message, state: FSMContext):
    if message.content_type == "contact":
        user = message.contact.user_id
    else:
        user = message.text
    user = await TgUser.get_or_none(id=user)

    if user:
        async with state.proxy() as data:
            playlist = await Playlist.get_or_none(id=data["choise"])
        await Shared.get_or_create(shared_to=user, playlist=playlist)
        await bot.send_message(
            chat_id=message.chat.id,
            text="An offer is placed. Will he accept it? Who knows.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
    else:
        await bot.send_message(
            chat_id=message.chat.id,
            text="This user is not registered here! Looser.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )

    await state.reset_state()
    await state.reset_data()


@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "aa", state="*"
)
async def accept_access(query: CallbackQuery, state: FSMContext):
    await state.set_state("accept_access")
    async with state.proxy() as data:
        shareds = (
            await Shared.filter(shared_to_id=query.message.chat.id)
            .order_by("id")
            .values_list("playlist__name", "id", "accepted")
        )
    if shareds.__len__() == 0:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="You have nothing to accept.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
        return
    data["shareds"] = shareds
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Accept any of those offers or go back:",
        reply_markup=create_inline_keyboard(buttons=shareds),
    )
    await state.set_state("accepting")


@dispatcher.callback_query_handler(state="accepting")
async def accepting_access(query: CallbackQuery, state: FSMContext):
    accepting = await Shared.get(id=query.data)
    accepting.accepted = not accepting.accepted
    await accepting.save()
    async with state.proxy() as data:
        shareds = data["shareds"]
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Any more?",
        reply_markup=create_inline_keyboard(buttons=shareds),
    )


@dispatcher.callback_query_handler(
    lambda callback_query: callback_query.data == "mys", state="*"
)
async def manage_shares(query: CallbackQuery, state: FSMContext):
    await state.set_state("delete_shares")
    shareds = (
        await Shared.filter(playlist__owner_id=query.message.chat.id)
        .order_by("id")
        .values_list("playlist__name", "shared_to__id", "id", "accepted")
    )
    if shareds.__len__() == 0:
        await bot.edit_message_text(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            text="You have no shared playlists.",
            reply_markup=create_inline_keyboard(
                [
                    {"Create new": "cr", "Choose active": "ch"},
                    {"Fren activities": "fr", "Delete old": "del"},
                    {"Retrieve": "rt"},
                ]
            ),
        )
        await state.reset_state()
        return
    async with state.proxy() as data:
        data["shareds_my"] = shareds
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Choose what to unshare:",
        reply_markup=create_inline_keyboard_shares(shareds),
    )


@dispatcher.callback_query_handler(state="delete_shares")
async def delete_share(query: CallbackQuery, state: FSMContext):
    accepting = await Shared.get(id=query.data)
    await accepting.delete()
    await bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        text="Done!",
        reply_markup=create_inline_keyboard(
            buttons=[
                {"Create new": "cr", "Choose active": "ch"},
                {"Fren activities": "fr", "Delete old": "del"},
                {"Retrieve": "rt"},
            ]
        ),
    )
