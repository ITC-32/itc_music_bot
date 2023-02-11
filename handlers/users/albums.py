from aiogram.dispatcher import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile
from sqlalchemy.orm import Session

from buttons import NEXT, PREV, CANCEL
from commands import COMMANDS
from loader import dp
from models import Album, Author, Music, AlbumMusic
from state import ChooseAlbumState


@dp.message_handler(text=COMMANDS["albums_list"])
async def albums_list(message: Message, state: FSMContext):
    with Session() as session:
        album = session.query(Album).first()
        album_author = session.query(Author).filter(
            Author.id == album.author
        ).first()
    await ChooseAlbumState.choose.set()
    await state.update_data(choose=2)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        PREV,
        InlineKeyboardButton("Посмотреть треки", callback_data=str(album.id)),
        NEXT
    )
    keyboard.add(CANCEL)
    await message.answer(
        f"Название: {album.name}\n"
        f"Автор: {album_author.full_name}\n"
        f"Дата создания: {album.created_date}\n"
        f"Дата рождение автора: {album_author.birth_date}",
        reply_markup=keyboard
    )


@dp.callback_query_handler(state=ChooseAlbumState.choose)
async def choose_album(callback: CallbackQuery, state: FSMContext):
    if callback.data == "cancel":
        await state.finish()
        await callback.bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )
    elif callback.data in ["next", "prev"]:
        async with state.proxy() as data:
            count = data["choose"]
        if callback.data == "next":
            with Session() as session:
                album = session.query(Album).limit(count)[-1]
            await state.update_data(choose=count+1)
        else:
            with Session() as session:
                if count <= 0:
                    count = 1
                if count == 1:
                    album = session.query(Album).first()
                else:
                    album = session.query(Album).limit(count-1)[-1]
            await state.update_data(choose=count-1)
        album_author = session.query(Author).filter(
            Author.id == album.author
        ).first()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            PREV,
            InlineKeyboardButton("Посмотреть треки", callback_data=str(album.id)),
            NEXT
        )
        keyboard.add(CANCEL)
        await callback.bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )
        await callback.bot.send_message(
            callback.from_user.id,
            f"Название: {album.name}\n"
            f"Автор: {album_author.full_name}\n"
            f"Дата создания: {album.created_date}\n"
            f"Дата рождение автора: {album_author.birth_date}",
            reply_markup=keyboard
        )
    else:
        musics_list = []
        with Session() as session:
            album_musics = session.query(AlbumMusic).filter(
                AlbumMusic.album_id == int(callback.data)
            ).all()
        if not album_musics:
            await callback.bot.send_message(
                callback.from_user.id,
                "Треков по этому альбому нет!"
            )
        else:
            with Session() as session:
                for music in album_musics:
                    found_music = session.query(Music).filter(
                        Music.id == music.music_id
                    ).first()
                    musics_list.append(found_music)
            for music in musics_list:
                await callback.bot.send_audio(
                    callback.from_user.id,
                    audio=InputFile(music.mp3_file_path)
                )
        await callback.bot.delete_message(
            callback.from_user.id,
            callback.message.message_id
        )
        await state.finish()
