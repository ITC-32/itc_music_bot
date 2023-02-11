from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import and_
from sqlalchemy.orm import Session

from commands import COMMANDS
from filters import IsAdmin
from loader import dp
from models import Album, Author
from state import AddAlbumState


@dp.message_handler(IsAdmin(), text=COMMANDS['add_album'])
async def add_album_command(message: Message):
    await AddAlbumState.name.set()
    await message.answer("Отлично! Отправьте имя альбома")


@dp.message_handler(IsAdmin(), state=AddAlbumState.name)
async def album_author(message: Message, state: FSMContext):
    await AddAlbumState.author.set()
    await state.update_data(name=message.text)
    keyboard = InlineKeyboardMarkup()
    with Session() as session:
        authors = session.query(Author).all()
    for author in authors:
        keyboard.add(InlineKeyboardButton(
            author.full_name, callback_data=str(author.id)
        ))
    await message.answer("Отлично! Выберите автора", reply_markup=keyboard)


@dp.callback_query_handler(state=AddAlbumState.author)
async def check_and_create(callback: CallbackQuery, state: FSMContext):
    author_id = int(callback.data)
    async with state.proxy() as data:
        album_name = data["name"]
    with Session() as session:
        album = session.query(Album).filter(and_(
            Album.author == author_id,
            Album.name == album_name
        )).first()
    if album:
        await callback.bot.send_message(
            callback.from_user.id,
            "Такой альбом у этого автора уже есть!"
        )
    else:
        with Session() as session:
            session.add(Album(name=album_name, author=author_id))
            session.commit()
        await callback.bot.send_message(
            callback.from_user.id,
            "Успешно создал!"
        )
    await state.finish()
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
