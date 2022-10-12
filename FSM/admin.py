from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types, Dispatcher

from create_bot import bot
from config import admin_id
from data_base.all_connection import main_thread_connection, db


#######################################################################################################################


class FSMtest(StatesGroup):
    amount = State()

async def get_new_test():
    await FSMtest.amount.set()

async def load_amount_new_test(message : types.Message, state: FSMContext):
    await state.finish()
    id_and_amount = message.text.split('_')
    await db.db_async_update_amount_test(id_and_amount[0], int(id_and_amount[1]), main_thread_connection)
    await message.answer('+')


#######################################################################################################################


class FSMmessage(StatesGroup):
    message = State()

async def get_message():
    await FSMmessage.message.set()

async def load_message(message: types.Message, state: FSMContext):
    await state.finish()
    await send_users(message)

async def send_users(message):
    ids = await db.db_get_ids(main_thread_connection)
    for id in ids:
        if id[0] == admin_id:
            continue
        await bot.send_message(id[0], message.text)
    await message.answer('+')


#######################################################################################################################
"""Register FSM"""


def register_FSM_admin(dp: Dispatcher):
    dp.register_message_handler(load_amount_new_test, state=FSMtest.amount)
    dp.register_message_handler(load_message, state=FSMmessage.message)