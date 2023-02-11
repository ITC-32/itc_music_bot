from aiogram.dispatcher import FSMContext
from aiogram.types import Message

from keyboards import users_keyboard
from loader import dp


@dp.message_handler(commands=['start'], commands_prefix="/!")
async def start_user(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("Привет, смертный! Выбери команду", reply_markup=users_keyboard)
