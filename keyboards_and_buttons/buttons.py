from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

inline_for_start_client = InlineKeyboardMarkup().\
    add(InlineKeyboardButton('🔗 Online Tribune', url='http://onlinetribune.info/'))

inline_for_menu = InlineKeyboardMarkup(row_width=1).\
    add(InlineKeyboardButton('📝 Персональні дані', callback_data='personal_data'), \
        InlineKeyboardButton('💶 Капуста', callback_data='money'))

inline_for_money = InlineKeyboardMarkup(row_width=1).\
    add(InlineKeyboardButton('Як поповнити 👛?', callback_data='top_up'))

inline_for_data = InlineKeyboardMarkup(row_width=1).\
    add(InlineKeyboardButton('Все вірно ✅   ', callback_data='all_correct'), \
        InlineKeyboardButton('Змінити ⁉', callback_data='change_data'))

inline_for_change_data = InlineKeyboardMarkup(row_width=1).add(InlineKeyboardButton('Змінити ⁉', callback_data='change_data'))

inline_howtosendalink = InlineKeyboardMarkup(row_width=1).\
    add(InlineKeyboardButton('Не знаю як це зробити 🤷', callback_data='send_link'))

inline_cancel = InlineKeyboardMarkup(row_width=1).\
    add(InlineKeyboardButton('Скасувати зміни', callback_data='cancel'))

inline_for_start_admin = InlineKeyboardMarkup(row_width=1).\
    add(InlineKeyboardButton('Додати тестів', callback_data='add_test'),
        InlineKeyboardButton('Переглянути логи', callback_data='show_log'),
        InlineKeyboardButton('Видалити логи', callback_data='clear_log'),
        InlineKeyboardButton('Вiдправити повiдомлення', callback_data='send_messages'))

inline_enter_data = InlineKeyboardMarkup(row_width=1).\
    add(InlineKeyboardButton('Ввести дані', callback_data='change_data'))