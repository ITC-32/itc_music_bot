from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from commands import COMMANDS
from config import Session
from loader import dp
from models import Music, Author, Genre
from state import SearchMusicState


@dp.message_handler(text=COMMANDS["search_music"])
async def search_music(message: Message):
    await SearchMusicState.search.set()
    await message.answer("Отлично! Отправьте имя трека")


@dp.message_handler(state=SearchMusicState.search)
async def search_result(message: Message, state: FSMContext):
    with Session() as session:
        musics = session.query(
            Music.id, Music.name, Music.duration,
            Author.full_name,
            Genre.name
        ).join(Author).join(Genre).filter(
            Music.name.contains(message.text)
        ).all()
    if not musics:
        await message.answer("Треки не найдены!")
        await state.finish()
        return
    await message.answer("Найденные треки")
    for music in musics:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            f"Скачать",
            callback_data=music[0]
        ))
        await message.bot.send_message(message.from_user.id,
                                       f"Название: {music[1]}\nАвтор: {music[3]}\n"
                                       f"Жанр: {music[4]}\nДлительность: {music[2]}",
                                       reply_markup=keyboard)
    await SearchMusicState.confirm.set()


@dp.callback_query_handler(state=SearchMusicState.confirm)
async def send_music(callback: CallbackQuery, state: FSMContext):
    await state.finish()
    with Session() as session:
        music = session.query(Music).filter(Music.id == int(callback.data)).first()
        music.downloads += 1
        session.commit()
    await callback.bot.send_audio(
        callback.from_user.id,
        audio=InputFile(music.mp3_file_path)
    )


@dp.message_handler(text=COMMANDS["popular_music"])
async def popular_music(message: Message):
    with Session() as session:
        popular_musics = session.query(Music).order_by(
            Music.downloads.desc()
        ).limit(5)
    await message.answer("5 самых популярных треков")
    for music in popular_musics:
        await message.bot.send_audio(
            message.from_user.id,
            audio=InputFile(music.mp3_file_path)
        )
