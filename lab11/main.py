import math
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from aiogram.utils.markdown import hcode
from aiogram import Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import StateFilter #чтоб функция функцию от слова Назад не вычисляла

import asyncio
import logging
from aiogram.client.default import DefaultBotProperties

TOKEN = "8703632186:AAEZFL2Y8abCu2QgbwaJ-150tx7LdOBaUUs"

# состояния
class FuncBuilder(StatesGroup):
    building = State()
    input_value = State()
    one_func = State()
    one_func_input = State()

#==================Кнопки==================
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Вывести выражение")],
            [KeyboardButton(text="Одна функция")]
        ],
        resize_keyboard=True
    )

def function_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1/x"), KeyboardButton(text="sqrt(x)"), KeyboardButton(text="exp(x)")],
            [KeyboardButton(text="Готово"), KeyboardButton(text="Вычислить")]
        ],
        resize_keyboard=True
    )

def one_function_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="1/x"), KeyboardButton(text="sqrt(x)"), KeyboardButton(text="exp(x)")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )

#==================Инициализация=====================
dp = Dispatcher(storage=MemoryStorage())
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

router = Router()
dp.include_router(router)

#=================обработка команд и сообщений========================

# обработка /start
@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите режим работы:", reply_markup=main_menu())

# глобальная обработка кнопки "Назад" (перемещена наверх со StateFilter("*"))
@router.message(StateFilter("*"), F.text == "Назад")
async def go_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите режим работы:", reply_markup=main_menu())

# обработка "Вывести выражение" (функция из нескольких делается)
@router.message(F.text == "Вывести выражение")
async def start_expression(message: Message, state: FSMContext):
    await state.update_data(functions=[])
    await message.answer("Добавьте функции в выражение:", reply_markup=function_keyboard())
    await state.set_state(FuncBuilder.building)

# обработка ввода функции
@router.message(FuncBuilder.building, F.text.in_({"1/x", "sqrt(x)", "exp(x)"}))
async def add_function(message: Message, state: FSMContext):
    data = await state.get_data()
    data["functions"].append(message.text)
    await state.update_data(functions=data["functions"])
    await message.answer(f"Добавлена функция: {message.text}")

# после ввода функции, ввод значения
@router.message(FuncBuilder.building, F.text == "Готово")
async def done_building(message: Message, state: FSMContext):
    await message.answer("Введите значение x:")
    await state.set_state(FuncBuilder.input_value)

# обработка введенного значения на предмет деления на ноль и корень из < 0
@router.message(FuncBuilder.input_value)
async def compute_expression(message: Message, state: FSMContext):
    try:
        x = float(message.text)
        data = await state.get_data()
        fx = x
        code_lines = ["Function ComputeValue(x)"] # тут начинается запись VBA кода
        code_lines.append("    ComputeValue = x")

        for func in data["functions"]:
            if func == "sqrt(x)":
                if fx < 0:
                    raise ValueError("Корень из значения < 0")
                fx = math.sqrt(fx)
                code_lines.append("\tComputeValue = Sqr(ComputeValue)")
            elif func == "1/x":
                if fx == 0:
                    raise ValueError("Деление на ноль")
                fx = 1 / fx
                code_lines.append("\tComputeValue = 1 / ComputeValue")
            elif func == "exp(x)":
                fx = math.exp(fx)
                code_lines.append("\tComputeValue = Exp(ComputeValue)")

        code_lines.append("End Function")
        vba_code = "\n".join(code_lines) # здесь заканчивается

        # вывод в сообщение
        await message.answer(f"Результат: <b>{fx}</b>\n\nVBA код:\n<pre>{hcode(vba_code)}</pre>", reply_markup=main_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка: {e}") # если ошибка - выводит текст ошибки

# обработка одной функции
@router.message(F.text == "Одна функция")
async def choose_one_func(message: Message, state: FSMContext):
    await state.set_state(FuncBuilder.one_func)
    await message.answer("Выберите функцию:", reply_markup=one_function_keyboard())

# после ввода одной функции
@router.message(FuncBuilder.one_func, F.text.in_({"1/x", "sqrt(x)", "exp(x)"}))
async def ask_for_x(message: Message, state: FSMContext):
    await state.update_data(func=message.text)
    await state.set_state(FuncBuilder.one_func_input)
    await message.answer("Введите значение x:")

# обработка введенного значения
@router.message(FuncBuilder.one_func_input)
async def compute_single_func(message: Message, state: FSMContext):
    try:
        x = float(message.text)
        data = await state.get_data()
        func = data["func"]
        if func == "sqrt(x)":
            if x < 0:
                raise ValueError("Корень из значения < 0")
            result = math.sqrt(x)
            code = "Sqr(x)"
        elif func == "1/x":
            if x == 0:
                raise ValueError("Деление на ноль")
            result = 1 / x
            code = "1 / x"
        elif func == "exp(x)":
            result = math.exp(x)
            code = "Exp(x)"
        await message.answer(f"Результат: <b>{result}</b>\n\nVBA код: <pre>{code}</pre>", reply_markup=main_menu())
        await state.clear()
    except Exception as e:
        await message.answer(f"Ошибка: {e}")

# запуск
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())