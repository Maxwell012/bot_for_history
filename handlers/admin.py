from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
import os

from keyboards_and_buttons.buttons import inline_for_start_admin
from keyboards_and_buttons.keyboards import kb_cancel
from config import admin_id
from FSM.admin import get_new_test, get_message, register_FSM_admin
from create_logger import create_logger


#######################################################################################################################


logger_admin = create_logger(__name__)

async def start_admin(message : types.Message):
    if admin_id == message.from_user.id:
        await message.answer('<b>Що робимо ❓</b>', reply_markup=inline_for_start_admin, parse_mode='html')
    else:
        await message.answer('<b>На жаль ви не адмін ❗</b>', parse_mode='html')


#######################################################################################################################


async def add_test(callback: types.CallbackQuery):
    try:
        await get_new_test()
        await callback.message.answer(
            'Відправ id та кількість тестів яку потрібно додати\n\n'
            f'<i>Приклад: {callback.message.chat.id}_5</i>',
            parse_mode='html',
            reply_markup=kb_cancel
        )
        await callback.answer()
    except Exception as ex:
        logger_admin.error('Error while added test', exc_info=True)

async def show_log(callback: types.CallbackQuery):
    try:
        for file in os.listdir("file_logs"):
            if file.endswith(".log"):
                if os.path.getsize(f"file_logs/{file}") == 0:
                    await callback.message.answer(f'{file} --- empty')
                else:
                    document = types.InputFile(f"file_logs/{file}")
                    await callback.message.answer_document(document=document)
        await callback.answer('Це всі файли з логами !')
    except Exception as ex:
        logger_admin.error('Error while read file of log', exc_info=True)

async def clear_log(callback: types.CallbackQuery):
    try:
        for file in os.listdir(f"file_logs"):
            with open(f"file_logs/{file}", 'w+') as f:
                f.seek(0)

        await callback.message.answer('+')
        await callback.answer()
    except Exception as ex:
        logger_admin.error('Error while clear file of log', exc_info=True)

async def send_messages(callback: types.CallbackQuery):
    try:
        await get_message()
        await callback.message.answer(
            '--- Відправ повiдомлення ---\n\n',
            parse_mode='html',
            reply_markup=kb_cancel
        )
        await callback.answer()
    except Exception as ex:
        logger_admin.error('Error while sending messages', exc_info=True)



#######################################################################################################################


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(start_admin, commands=['admin'])
##################################################################
    dp.register_callback_query_handler(add_test, Text('add_test'))
    dp.register_callback_query_handler(show_log, Text('show_log'))
    dp.register_callback_query_handler(clear_log, Text('clear_log'))
    dp.register_callback_query_handler(send_messages, Text('send_messages'))

    register_FSM_admin(dp)