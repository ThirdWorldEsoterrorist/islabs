import asyncio
import requests
import xml.etree.ElementTree as ET
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart, Command

TOKEN = 'вставьте-сюда-ваш-токен'
PROXY_URL = "socks5://182.48.78.141:8008"


# Основная функция для парсинга (теперь с ЦБ РФ)
def get_currency(*names):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    proxies = {
        "http": PROXY_URL,
        "https": PROXY_URL
    }

    try:
        response = requests.get(
            "http://www.cbr.ru/scripts/XML_daily.asp",
            headers=headers,
            proxies=proxies,
            timeout=10
        )
        response.raise_for_status()

        # Разбираем XML-ответ от ЦБ РФ
        root = ET.fromstring(response.content)

    except (requests.RequestException, ET.ParseError) as e:
        print(f"Ошибка при получении данных: {e}")
        return []

    data = []
    backup = []

    names_upper = [n.upper() for n in names]

    # Ищем все теги <Valute> в XML-документе
    for valute in root.findall('Valute'):
        # Извлекаем нужные данные из тегов
        char_code = valute.find('CharCode').text
        name = valute.find('Name').text
        nominal = float(valute.find('Nominal').text)

        # Значение приходит с запятой, меняем на точку для float
        value_str = valute.find('Value').text.replace(',', '.')
        value = float(value_str)

        # Высчитываем стоимость ровно за 1 единицу валюты
        price_per_unit = round(value / nominal, 4)

        curr_data = {
            'name': name,
            'code': char_code,
            'price': price_per_unit,
            'exchange_curr': 'RUB'
        }

        # Проверяем совпадение по коду или по полному имени
        if char_code in names_upper or name.upper() in names_upper:
            data.append(curr_data)
        backup.append(curr_data)

    if data:
        return data
    return backup


router = Router()


# ================= ОБРАБОТЧИКИ КОМАНД ======================

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Введи код валюты (например, USD или EUR) или используй команду /rate USD.")


@router.message(Command("rate"))
async def rate_command(message: types.Message):
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer("Пожалуйста, укажите код валюты после команды. Пример: /rate USD")
        return

    currency_code = parts[1].upper()
    prices = get_currency()

    if not prices:
        await message.answer("Извините, сервис ЦБ РФ временно недоступен.")
        return

    for currency in prices:
        if currency['code'] == currency_code or currency['name'].upper() == currency_code:
            await message.answer(
                f"{currency['name']} ({currency['code']}) - {currency['price']} {currency['exchange_curr']}")
            return

    await message.answer(f"Валюта с кодом '{currency_code}' не найдена в текущем списке.")


@router.message()
async def parse(message: types.Message):
    prices = get_currency()
    if not prices:
        await message.answer("Извините, сервис получения курсов временно недоступен.")
        return

    user_input = message.text.upper()
    for currency in prices:
        if currency['code'] == user_input or currency['name'].upper() == user_input:
            await message.answer(
                f"{currency['name']} ({currency['code']}) - {currency['price']} {currency['exchange_curr']}")
            break
    else:
        await message.answer(
            f"К сожалению, валюта '{message.text}' не найдена.\n"
            f"Попробуйте ввести другой буквенный код или проверьте правильность написания введенного."
        )


async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
