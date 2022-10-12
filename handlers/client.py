from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher

from keyboards_and_buttons.keyboards import kb_start_client
from keyboards_and_buttons.buttons import inline_for_start_client, inline_enter_data, \
                                          inline_for_money, inline_for_menu, inline_for_change_data
from FSM.client import enter_data, enter_link, register_FSM_client
from data_base.all_connection import main_thread_connection, db


#######################################################################################################################


async def start(message : types.Message):
    await message.answer('👋 Привіт\n '
                         'Я можу пройти будь-який тест з цієї сторінки', \
                         reply_markup=inline_for_start_client)
    await message.answer('Let`s go...', reply_markup=kb_start_client)


#######################################################################################################################


async def test(message : types.Message):
    check_id = await db.db_check_id(message.from_user.id, main_thread_connection)
    if check_id:
        amount_test = await db.db_get_amount_test(message.from_user.id, main_thread_connection)
        if amount_test <= 0:
            await message.answer('В тебе не залишилося більше спроб проходження тесту ❗',
                                 reply_markup=inline_for_money)
        else:
            await enter_link(message)
    else:
        await message.answer('📝 Вам спочатку треба заповнити персональні дані '
                             'які будуть відправлятися після проходження тесту)',
                             reply_markup=inline_enter_data)

async def settings(message : types .Message):
    await message.answer('Що ви бажаєте зробити ❓', reply_markup=inline_for_menu)

async def contacts(message : types.Message):
    await message.answer('✍ Пиши @david_krbnv з будь-яких питань:\n' 
                                  '🔨 неполадки в роботі сервісу;\n'
                                  '💡 пропозиції та зауваження;\n'
                                  '➕ підтримка нової мови;\n'
                                  '💸 повернення грошей;\n'
                                  '😉 будь-що інше...\n\n'
                                  f'<i>Твій ідентифікатор: {message.chat.id}</i>', parse_mode='html')
    await message.answer_contact('+48786467177', '🇺🇦 Admin')


#######################################################################################################################


# async def send_link(callback: types.CallbackQuery, state: FSMContext):
#     photo = types.InputFile("foto/foto_ex_link.png")
#     caption = 'Мені потрібне посилання яке буде вказувати на схожу сторінку як ця ⬆.\n\n' \
#               'Коли я вчився на дистанційці, ' \
#               'нам вчитель історії відправляв в коментарях Microsoft Teams посилання на тест, ' \
#               'можливо у вас так само 🫠'
#     await callback.message.answer_photo(photo=photo, caption=caption, reply_markup=kb_cancel)
#     await callback.message.delete()
#     await callback.answer()

async def personal_data(callback: types.CallbackQuery):
    await callback.answer()
    data = await db.db_get_data(callback.message.chat.id, main_thread_connection)
    if data:
        await callback.message.answer(f'🔹 Прізвище: {data[0]}\n'
                                      f'🔹 Email: {data[1]}\n'
                                      f'🔹 Час проходження: {data[2]} секунд\n'
                                      f'🔹 К-ть неправильних відповідей: {data[3]}',
                                      reply_markup=inline_for_change_data)
    else:
        await enter_data(callback.message, False)

# @dp.callback_query_handler(Text=('change_data'))
async def change_data(callback: types.CallbackQuery):
    await enter_data(callback.message)
    await callback.answer()

async def money_callback(callback: types.CallbackQuery):
    free_test = await db.db_get_amount_test(callback.message.chat.id, main_thread_connection)

    await callback.message.answer(f'В тебе залишилося - {free_test} - спроб проходжень тесту ❗',
                                      reply_markup=inline_for_money)
    await callback.answer()

async def money_commands(message: types.Message):
    free_test = await db.db_get_amount_test(message.chat.id, main_thread_connection)

    await message.answer(f'В тебе залишилося - {free_test} - спроб проходжень тесту ❗',
                                      reply_markup=inline_for_money)


#######################################################################################################################


# @dp.callback_query_handler(Text=('top_up'))
async def top_up(callback: types.CallbackQuery):
    await callback.message.answer('🔹 Моно - <a>https://send.monobank.ua/7Pxyk7KLMJ</a>\n\n'
                                  '🔹 Приват - <a>https://privatbank.ua/ru/sendmoney?payment=fe75455d04</a>\n\n'
                                  '<b>1 тест      ---     15 грн\n'
                                  '3 теста     ---     36 грн\n'
                                  '7 тестів    ---     70 грн</b>\n\n'
                                  'В повідомлені платежа, відправте свій індентифікатор. '
                                  'Після оплати через декілька хвилин я зарахую вам тести ‼\n\n'
                                  f'<i>Твій індентифікатор: <b>{callback.message.chat.id}</b></i>\n\n'
                                  'P.S.: трохи пізніше оплата стане автоматизованою !',
                                  parse_mode='html', disable_web_page_preview=True)
    await callback. answer()

async def what_send_link(message: types.Message):
    await message.answer()


#######################################################################################################################


# @dp.callback_query_handler(Text('arr_correct'))
async def all_correct(callback : types.CallbackQuery):
    await callback.message.answer('Добре, записав 👌', reply_markup=kb_start_client)
    await callback.message.delete()
    await callback.answer()













#######################################################################################################################


def register_handlers_client(dp : Dispatcher):
    dp.register_message_handler(start, commands=['start', 'help'])
    ##############################################################
    dp.register_message_handler(test, commands=['test'])
    dp.register_message_handler(test, text='🏁 Тест')

    dp.register_message_handler(settings, commands=['settings'])
    dp.register_message_handler(settings, text='⚙ Налаштування')

    dp.register_message_handler(contacts, commands=['support'])
    dp.register_message_handler(contacts, text="✍ Зв'язок")
    ##############################################################
    # dp.register_callback_query_handler(send_link, Text('send_link'), state=FSMlink.link)
    dp.register_callback_query_handler(personal_data, Text('personal_data'))
    dp.register_callback_query_handler(change_data, Text('change_data'))
    dp.register_message_handler(money_commands, commands=['balance'])
    dp.register_callback_query_handler(money_callback, Text('money'))
    ##############################################################
    dp.register_callback_query_handler(top_up, Text('top_up'))
    ##############################################################
    dp.register_callback_query_handler(all_correct, Text('all_correct'))

    register_FSM_client(dp)