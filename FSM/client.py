from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from threading import Thread

from keyboards_and_buttons.keyboards import kb_cancel, kb_start_client
from keyboards_and_buttons.buttons import inline_for_data
from solving_the_test.main import time_for_test, main
from config import token
from data_base.all_connection import main_thread_connection, db


#######################################################################################################################
"""FSM machine for changing personal data"""


class FSMuser(StatesGroup):
    surname = State()
    email = State()
    time = State()
    incorrect_answer = State()

async def enter_data(message : types.Message, message_delete=True):
    await FSMuser.surname.set()
    await message.answer(
        'Якщо ви передумаєте вводити дані, то напишіть "відміна"\n\n'
        '<b>Введіть ваше прізвище</b>\n'
        '<i>Приклад: Melnyk</i>',
        reply_markup=kb_cancel,
        parse_mode='html')

    if message_delete:
        await message.delete()


async def cancel_handler(message : types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('Добре 👌', reply_markup=kb_start_client)

async def load_surname(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['surname'] = message.text
        await FSMuser.next()
        await message.answer('<b>Тепер ваш email</b>\n'
                             '<i>Приклад: example@gmail.com</i>', parse_mode='html')

async def load_email(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['email'] = message.text
        await FSMuser.next()
        await message.answer('<b>К-ть секунд на проходження одного запитання</b>\n\n'
                             '<i>Рекомендую виставляти значення близьке до дійсного, щоб вчитель нічого не запідозрив</i>\n'
                             '<i>Приклад: 15</i>', parse_mode='html')

async def load_time_invalid(message: types.Message):
    """
    If time is invalid
    """
    return await message.reply("‼ Введіть будь ласка цілу цифру з проміжку [0, 240] ‼")

async def load_time(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = int(message.text)
        await FSMuser.next()
        await message.answer('<b>К-ть помилок в тестуванні</b>\n'
                             '<i>Приклад: 2</i>', parse_mode='html')

async def load_incorrect_answer_invalid(message: types.Message):
    """
    If incorrect_answer is invalid
    """
    return await message.reply("‼ Введіть будь ласка цілу цифру з проміжку [0, 99] ‼")

async def load_incorrect_answer(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['incorrect_answer'] = int(message.text)
        await message.answer(f'🔹 Прізвище: {data["surname"]}\n'
                             f'🔹 Email: {data["email"]}\n'
                             f'🔹 Час проходження: {data["time"]} секунд\n'
                             f'🔹 К-ть неправильних відповідей: {data["incorrect_answer"]}',
                             reply_markup=inline_for_data)
        await db.db_add_data(message.from_user.id, data, main_thread_connection)
    await state.finish()


#######################################################################################################################
"""test execution"""


class FSMlink(StatesGroup):
    link = State()

async def enter_link(message):
    await message.answer('<b>Відправте посилання на тест 🔗</b>\n\n'
                         '<i>* Приклад: http://onlinetribune.info/testi-do-seminaru-1/\n'
                         '* Якщо передумали проходити, пишіть "відміна"</i>',
                         reply_markup=kb_cancel, parse_mode='html')
    await FSMlink.link.set()

async def load_link(message : types.Message, state: FSMContext):
    """Receives a link and performs a test"""

    await state.finish()
    await start_test(message)

async def start_test(message: types.Message):
    data_user = await db.db_get_data(message.from_user.id, main_thread_connection)
    time_for_pass_test = await time_for_test(message.text, data_user[2])
    await message.answer(time_for_pass_test, reply_markup=kb_start_client)

    data = {
        'surname': data_user[0],
        'email': data_user[1],
        'time': data_user[2],
        'incorrect_answer': data_user[3],
        'link': message.text,
        'token': token,
        'chat_id': message.chat.id
    }

    await db.db_async_update_amount_test(message.from_user.id, -1, main_thread_connection)

    Thread(target=main, args=(data, )).start()


#######################################################################################################################
"""Register FSM"""


def register_FSM_client(dp: Dispatcher):
    dp.register_message_handler(enter_data, text='Персональні дані', state=None)
    dp.register_message_handler(cancel_handler, state='*', commands='Відміна')
    dp.register_message_handler(cancel_handler, Text(equals='Відміна', ignore_case=True), state='*')
    dp.register_message_handler(load_surname, state=FSMuser.surname)
    dp.register_message_handler(load_email, state=FSMuser.email)
    dp.register_message_handler(load_time_invalid,
                                lambda message: not message.text.isdigit()
                                                or (message.text.isdigit()
                                                    and (int(message.text) < 0
                                                         or int(message.text) > 240)),
                                state=FSMuser.time)
    dp.register_message_handler(load_time,
                                lambda message: message.text.isdigit()
                                                and int(message.text) >= 0
                                                and int(message.text) <= 240,
                                state=FSMuser.time)
    dp.register_message_handler(load_incorrect_answer_invalid,
                                lambda message: not message.text.isdigit()
                                                or (message.text.isdigit()
                                                    and (int(message.text) < 0
                                                         or int(message.text) > 99)),
                                state=FSMuser.incorrect_answer)
    dp.register_message_handler(load_incorrect_answer,
                                lambda message: message.text.isdigit()
                                                and int(message.text) >= 0
                                                and int(message.text) <= 99,
                                state=FSMuser.incorrect_answer)
    ##############################################################
    dp.register_message_handler(load_link, state=FSMlink.link)