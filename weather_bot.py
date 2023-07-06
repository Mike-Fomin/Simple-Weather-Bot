import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, CallbackQueryHandler
from config import TOKEN, API

ask_reply_weather = InlineKeyboardMarkup([
        [InlineKeyboardButton("Новочебоксарск", callback_data='Novocheboksarsk')],
        [InlineKeyboardButton("Москва", callback_data='Moscow')],
        [InlineKeyboardButton("Ханой", callback_data='Hanoi')]
    ])


def get_weather(city):
    emoji_codes = {
        'Thunderstorm': '\U000026C8',
        'Drizzle': '\U0001F326',
        'Rain': '\U0001F327',
        'Snow': '\U0001F328',
        'Mist': '\U0001F32B',
        'Fog': '\U0001F32B',
        'Clear': '\U00002600',
        'Clouds': '\U00002601'
    }
    weather_codes = {
        'Thunderstorm': 'Гроза',
        'Drizzle': 'Морось',
        'Rain': 'Дождь',
        'Snow': 'Снег',
        'Mist': 'Дымка',
        'Fog': 'Туман',
        'Clear': 'Ясно',
        'Clouds': 'Облачно'
    }

    try:
        params = {
            'units': 'metric',
            'lang': 'ru',
            'appid': API,
            'q': city
        }
        response = requests.get(url=f'https://api.openweathermap.org/data/2.5/weather', params=params)
        data = response.json()

        name = data['name']
        temp = round(data['main']['temp'], 1)
        feels = round(data['main']['feels_like'], 1)
        if data['weather'][0]['main'] in emoji_codes:
            weather_em = emoji_codes[data['weather'][0]['main']]
            weather_cond = weather_codes[data['weather'][0]['main']]
        else:
            weather_em = '\U0000F5FF'
            weather_cond = 'не вижу, что там за окном'
        return f"{name}\n{weather_cond}  {weather_em}\nТемпература: {temp}\nОщущается как {feels}"
    except:
        return 'Введите название города еще раз латиницей'


async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Привет, {user.first_name}!\n"
                                        f"Выбери город из списка, чтобы узнать погоду.\n"
                                        f"Либо введи название другого города латиницей через '/'.\n"
                                        f"Пример: /london",
                                   reply_markup=ask_reply_weather)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Это простой погодный бот."
                                    "Чтобы запросить погоду отправьте в чат команду /weather")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Привет, {user.first_name}!\n"
                                        f"Давай начнем использовать бота!\n"
                                        f"Введи команду /weather")


async def weather_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        city = update.message.text
    except:
        city = update.callback_query.data
        await update.callback_query.edit_message_text(get_weather(city), reply_markup=ask_reply_weather)
    else:
        if city.startswith('/'):
            city = city[1:]
        cities = {
            'Новочебоксарск': 'Novocheboksarsk',
            'Москва': 'Moscow',
            'Ханой': 'Hanoi'
        }
        if city in cities:
            city = cities[city]
        await context.bot.send_message(chat_id=update.effective_chat.id, text=get_weather(city))


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CallbackQueryHandler(weather_response))
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("weather", weather))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.COMMAND, weather_response))

    application.run_polling()


if __name__ == "__main__":
    main()
