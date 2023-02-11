from aiogram.dispatcher.filters.state import StatesGroup, State


class CreateMusicState(StatesGroup):
    name = State()
    genre = State()
    duration = State()
    author = State()
    music_raw = State()


class CreateAuthorState(StatesGroup):
    full_name = State()
    birth_date = State()


class CreateGenreState(StatesGroup):
    name = State()


class DeleteAuthorState(StatesGroup):
    callback_query = State()


class SearchMusicState(StatesGroup):
    search = State()
    confirm = State()


class AddAlbumState(StatesGroup):
    name = State()
    author = State()


class AddAlbumMusicState(StatesGroup):
    album_id = State()
    music_id = State()


class ChooseAlbumState(StatesGroup):
    choose = State()
