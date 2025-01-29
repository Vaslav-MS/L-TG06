import asyncio, aiohttp, logging, requests, sqlite3
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from config import TOKEN, EXCHANGERATEAPIKEY
bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

button_registr = KeyboardButton(text='Регистрация')
button_exchange = KeyboardButton(text='Курс валют')
button_soviets = KeyboardButton(text='Советы по экономике')
button_finances = KeyboardButton(text='Учёт расходов')
keyboard = ReplyKeyboardMarkup(keyboard=[
    [button_registr, button_exchange],
    [button_soviets, button_finances]], resize_keyboard=True)

conn = sqlite3.connect('user.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  telegram_id INTEGER UNIQUE,
                  name TEXT NOT NULL,
                  category1 TEXT,
                  category2 TEXT,
                  category3 TEXT,
                  expenses1 REAL,
                  expenses2 REAL,
                  expenses3 REAL)''')
conn.commit()

class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()

@dp.message(F.text == 'Регистрация')
async def registration(message: Message):
    telegram_id = message.from_user.id
    name = message.from_user.full_name
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()
    if user:
        await message.answer('Вы уже зарегистрированы!')
    else:
        cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
        conn.commit()
        await message.answer('Вы успешно зарегистрированы!')

@dp.message(F.text == 'Курс валют')
async def exchange_rate(message: Message):
    url = f'https://v6.exchangerate-api.com/v6/{EXCHANGERATEAPIKEY}/latest/USD'
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code != 200:
            await message.answer('Ошибка получения курса валют!')
            return
        usd_to_rub = data['conversion_rates']['RUB']
        usd_to_eur = data['conversion_rates']['EUR']
        eur_to_rub = usd_to_rub / usd_to_eur
        await message.answer(f'USD - {usd_to_rub:.2f} RUB\n'
                             f'EUR - {eur_to_rub:.2f} RUB')
    except:
        await message.answer('Произошла ошибка')

@dp.message(CommandStart)
async def start(message: Message):
    await message.answer('Привет! Это бот — личный финансовый помощник Нажми на одну из кнопка в миню:', reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
