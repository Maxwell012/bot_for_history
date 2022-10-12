from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

kb_start_client = ReplyKeyboardMarkup(resize_keyboard=True).row(
    KeyboardButton('🏁 Тест'),
    KeyboardButton('⚙ Налаштування')
).add(
    KeyboardButton("✍ Зв'язок")
)

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton('Відміна'))

