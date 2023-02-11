from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from sqlalchemy import and_

from commands import COMMANDS
from config import Session
from filters import IsAdmin
from loader import dp
from models import Album, Music, AlbumMusic
from state import AddAlbumMusicState


@dp.message_handler(IsAdmin(), text=COMMANDS["add_music_album"])
async def add_music_album(message: Message):
    await AddAlbumMusicState.album_id.set()
    with Session() as session:
        albums = session.query(Album).all()
    keyboard = InlineKeyboardMarkup()
    for album in albums:
        keyboard.add(InlineKeyboardButton(
            album.name,
            callback_data=str(album.id)
        ))
    await message.answer("Отлично! Выберите альбом", reply_markup=keyboard)


@dp.callback_query_handler(state=AddAlbumMusicState.album_id)
async def check_and_create(callback: CallbackQuery, state: FSMContext):
    await state.update_data(album_id=int(callback.data))
    await callback.bot.delete_message(
        callback.from_user.id,
        callback.message.message_id
    )
    keyboard = InlineKeyboardMarkup()
    with Session() as session:
        musics = session.query(Music).all()
    if not musics:
        await callback.bot.send_message(
            callback.from_user.id,
            "Дурак! Треков же нет! Попробуй теперь заново!"
        )
        await state.finish()
        return
    await AddAlbumMusicState.music_id.set()
    for music in musics:
        keyboard.add(InlineKeyboardButton(
            music.name,
            callback_data=str(music.id)
        ))
    await callback.bot.send_message(
        callback.from_user.id,
        "Отлично! Выберите трек",
        reply_markup=keyboard
    )


@dp.callback_query_handler(state=AddAlbumMusicState.music_id)
async def check_and_create(callback: CallbackQuery, state: FSMContext):
    music_id = int(callback.data)
    async with state.proxy() as data:
        album_id = data["album_id"]
    with Session() as session:
        album_music = session.query(AlbumMusic).filter(and_(
            AlbumMusic.music_id == music_id,
            AlbumMusic.album_id == album_id
        )).first()
    if album_music:
        await callback.bot.send_message(
            callback.from_user.id,
            "Трек уже добавлен в этот альбом!"
        )
    else:
        with Session() as session:
            session.add(AlbumMusic(album_id=album_id, music_id=music_id))
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
