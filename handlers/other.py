from aiogram import types, Dispatcher

from keyboards_and_buttons.keyboards import kb_start_client


#######################################################################################################################


async def roma(message : types.Message):
    if message.from_user.id == 504320960:
        await message.answer('👋 <b>Салам, халявных пять тестов тебе</b> 😂\n\n'
                             '<i>P.S.: я знаю что тебе они нахер не нужны, '
                             'но спасибо тебе за моральныю помощь в организации этого бота ❗</i>',
                             reply_markup=kb_start_client, parse_mode='html')

async def trash(message : types.Message):
    await message.answer('Хз що це, спробуй ще раз 🤷', reply_markup=kb_start_client)


#######################################################################################################################


def register_handlers_other(dp : Dispatcher):
    dp.register_message_handler(roma, text='я тут')
    dp.register_message_handler(trash)