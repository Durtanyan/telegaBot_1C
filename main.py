from aiogram import Bot, Dispatcher
from aiogram.filters import Command  # type: ignore
from aiogram.types import Message
import logging
import called_functions
import config
import text_constants

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
BOT_TOKEN = config.BOT_TOKEN
TRUE_MESSAGEREGISTRATION = text_constants.TRUE_MESSAGEREGISTRATION
FALSE_MESSAGEREGISTRATION = text_constants.FALSE_MESSAGEREGISTRATION
HELP_MESSAGE = text_constants.HELP_MESSAGE
names_available_reports = text_constants.NAMES_AVAILABLE_REPORTS


# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


logging.basicConfig(level=logging.INFO, filename='msg.log')


# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    user_name = message.chat.username
    chat_id = message.chat.id
    add_user_in_db = called_functions.add_user_in_db(user_name, chat_id)
    if add_user_in_db:
        logging.info(f'{user_name} зарегистрировался в системе')
        await message.answer(f'Привет, {user_name}! {TRUE_MESSAGEREGISTRATION}\n{HELP_MESSAGE}')
    else:
        logging.info(
            f'{user_name} пытался повторно зарегистрироваться в системе.')
        await message.answer(f'Прошу прощения, {user_name}! {FALSE_MESSAGEREGISTRATION}')
    url = called_functions.get_image_cat()
    await bot.send_photo(chat_id, url)


# Этот хэндлер будет срабатывать на команду "/help
async def process_help_command(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    logging.info(f'{user_name} вызвал команду - help.')
    await bot.send_message(chat_id, HELP_MESSAGE)


# Этот хэндлер будет срабатывать на команду "/command1"
# Просто выводит список доступных для подписки отчетов с их номерами
async def process_command_1(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    logging.info(
        f'{user_name} Воспользовался просмотром доступных для подписки отчетов.')
    list_available_reports = [str(i + 1) + ". " + names_available_reports[i]
                              for i in range(len(names_available_reports))]
    await bot.send_message(chat_id, "\n".join(list_available_reports))


# Этот хэндлер будет срабатывать на команду "/command2"
async def process_command_2(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    logging.info(
        f'{user_name} Получил отчеты по подписке.')
    await message.answer('Тест. Получены отчеты по подписке.')


# Этот хэндлер будет срабатывать на команду "/command3"
async def process_command_3(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    data_user = called_functions.unsubscribe_from_receiving_reports(user_name)
    logging.info(
        f'{user_name} Отписался от получения отчетов: {data_user}')
    await bot.send_message(chat_id, 'Тест. Вы отписались от получения отчетов по подписке.')


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения
# кроме тех команд, что расположены выше по регистрации
# Валидные данные это номера доступных для подписки отчетов
# Все остальное невалидно.
async def send_echo(message: Message):
    user_name = message.chat.username
    chat_id = message.chat.id
    # Считываем сообщение пользователя из телеги
    list_data = message.text.split(" ")
    try:
        # Преобразуем в список чисел
        # При ошибке уходим в исключения
        list_int = list(map(int, list_data))
        list_int.sort()
        # Из списка доступных отчетов получает их номера
        list_index_available_reports = [
            i + 1 for i in range(len(names_available_reports))]
        # Все элементы введенные пользователем должны быть в списке номеров доступных к подписке отчетов
        if all([i in list_index_available_reports for i in list_int]):
            # Списки равны - идем в БД и заполняем, ищем пользователя и заполняем
            # второй параметр из списка полученных отчетов. [chat_id, []]
            called_functions.add_reports_to_subscription(user_name, list_int)
            logging.info(
                f'{user_name} Подписался на получение отчетов: {list_data}')
            await bot.send_message(chat_id, text_constants.SUBSCRIPTION_MESSAGE)
        else:
            logging.info(
                f'{user_name} Ввел данные незарегистрированных отчетов: {list_data}')
            await bot.send_message(chat_id, text_constants.INVALID_DATA)
    except:
        broken_data = text_constants.BROKEN_DATA
        logging.info(
            f'{user_name} Ввел невалидные данные: {list_data}')
        await bot.send_message(chat_id, broken_data)


# Регистрируем хэндлеры
dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(process_command_1, Command(commands='command1'))
dp.message.register(process_command_2, Command(commands='command2'))
dp.message.register(process_command_3, Command(commands='command3'))
dp.message.register(send_echo)


if __name__ == '__main__':
    dp.run_polling(bot)
