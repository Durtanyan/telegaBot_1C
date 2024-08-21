from aiogram import Bot, Dispatcher
from aiogram.filters import Command  # type: ignore
from aiogram.types import Message
import logging
import pprint
import called_functions
import config
import text_constants

# Константы, которые используются в хендлерах
BOT_TOKEN = config.BOT_TOKEN
QUERY_ADMINISTRATOR = text_constants.QUERY_ADMINISTRATOR
TRUE_MESSAGEREGISTRATION = text_constants.TRUE_MESSAGEREGISTRATION
FALSE_MESSAGEREGISTRATION = text_constants.FALSE_MESSAGEREGISTRATION
HELP_MESSAGE = text_constants.HELP_MESSAGE
PROHIBITION_PERMISSION = text_constants.PROHIBITION_PERMISSION
names_available_reports = text_constants.NAMES_AVAILABLE_REPORTS


# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Подключаем логгинг
logging.basicConfig(level=logging.INFO, filename='msg.log',
                    format="%(asctime)s %(levelname)s %(message)s")


# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    user_name = message.chat.username
    chat_id = message.chat.id
    add_user_in_db = called_functions.add_user_in_db(user_name, chat_id)
    if add_user_in_db:
        logging.info(
            f'{user_name} отправил запрос администратору на регистрацию в системе.')
        await message.answer(f'Привет, {user_name}! {QUERY_ADMINISTRATOR}\n{HELP_MESSAGE}')
        await bot.send_message(text_constants.LIST_ID_ADMINISTRATOR[0], f'{user_name} подал заявку на регистрацию.')
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
    check_resolution = called_functions.check_resolution(user_name)
    if check_resolution:
        logging.info(f'{user_name} вызвал команду - help.')
        await bot.send_message(chat_id, HELP_MESSAGE)
    else:
        logging.info(
            f'{user_name} пытался вызвать команду - help. Запрет использования БД')
        await bot.send_message(chat_id, PROHIBITION_PERMISSION)


# Этот хэндлер будет срабатывать на команду "/command1"
# Просто выводит список доступных для подписки отчетов с их номерами
async def process_command_1(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    check_resolution = called_functions.check_resolution(user_name)
    if check_resolution:
        logging.info(
            f'{user_name} Воспользовался просмотром доступных для подписки отчетов.')
        list_available_reports = [str(i + 1) + ". " + names_available_reports[i]
                                  for i in range(len(names_available_reports))]
        await bot.send_message(chat_id, "\n".join(list_available_reports))
    else:
        logging.info(
            f'{user_name} пытался вызвать просмотр доступных отчетов. Запрет использования БД')
        await bot.send_message(chat_id, PROHIBITION_PERMISSION)


# Этот хэндлер будет срабатывать на команду "/command2"
# Либо выводит отчеты по подписке пользователю, либо сообщение об отказе,
# если администратор не добавил право просмотра пользователю.
async def process_command_2(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    check_resolution = called_functions.check_resolution(user_name)
    if check_resolution:
        logging.info(
            f'{user_name} Получил отчеты по подписке.')
        await bot.send_message(chat_id, called_functions.get_subscription_reports(user_name))
    else:
        logging.info(
            f'{user_name} пытался получить отчеты. Запрет использования БД')
        await bot.send_message(chat_id, PROHIBITION_PERMISSION)


# Этот хэндлер будет срабатывать на команду "/command3"
# Либо очищает список подписки на отчеты, возможность создать новый список сохраняется,
# либо выводит сообщение о запрете, если администратор не добавил прав пользователю.
async def process_command_3(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    check_resolution = called_functions.check_resolution(user_name)
    if check_resolution:
        data_user = called_functions.unsubscribe_from_receiving_reports(
            user_name)
        logging.info(
            f'{user_name} Отписался от получения отчетов: {data_user}')
        await bot.send_message(chat_id, 'Тест. Вы отписались от получения отчетов по подписке.')
    else:
        logging.info(
            f'{user_name} пытался отписаться от получения отчетов. Запрет использования БД')
        await bot.send_message(chat_id, PROHIBITION_PERMISSION)


# Этот хэндлер будет срабатывать на команду "/get_report_for_admin"
# Получение админом отчета по всем пользователям бота
async def process_command_get_report_for_admin(message: Message):
    chat_id = message.chat.id
    user_name = message.chat.username
    report_permissions = called_functions.get_report_permissions(
        user_name)
    logging.info(
        f'{user_name} администратор выполнил команду /get_report_for_admin.')
    await bot.send_message(chat_id, report_permissions)


# Этот хендлер срабатывает на команду /add_view [логин пользователя]
# Добавляет пользователю права на работу с БД - подписка на отчеты,
# просмотр отчетов, доступны стандартные команды и тд.
# Хендлер доступен только администратору бота. см.  text_constants.LIST_ID_ADMINISTRATOR
async def process_command_add_right_view_reports(message: Message):
    user_name = message.chat.username
    chat_id = message.chat.id
    list_id_admins = text_constants.LIST_ID_ADMINISTRATOR
    if chat_id in list_id_admins:
        list_data = message.text.split(" ")
        add_view_reports = called_functions.add_view_reports(list_data[1])
        if add_view_reports:
            logging.info(
                f'{user_name} администратор выполнил команду дал пользователю {list_data[1]} право пользователя БД.')
            await bot.send_message(chat_id, f'Пользователю {list_data[1]} добавлены права пользователя БД.')
            chat_user_id = called_functions.get_user_id(list_data[1])
            await bot.send_message(text_constants.LIST_ID_ADMINISTRATOR[0], f'{list_data[1]}, администратор добавил Вам права пользователя БД.\
                                   теперь Вы можете получать отчеты по подписке.')
            logging.info(
                f'Пользователю {list_data[1]} отправлено сообщение о добавлении права пользователя БД.')
        else:
            await bot.send_message(chat_id, f'Не удачная попытка добавить права пользователя ДБ для {list_data[1]}')
            logging.info(
                f'Пользователь {user_name} пытался изменить права пользователя {list_data[1]}. Неудачно. Отсутствуют права администратора БД')
    else:
        logging.info(
            f'Для пользователя {list_data[1]}, была попытка изменить прва')
        await bot.send_message(chat_id, text_constants.PROHIBITION_PERMISSION)


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения
# кроме тех команд, что расположены выше по регистрации
# Валидные данные это номера доступных для подписки отчетов
# Все остальное невалидно.
async def send_echo(message: Message):
    user_name = message.chat.username
    chat_id = message.chat.id
    # Считываем сообщение пользователя из телеги
    check_resolution = called_functions.check_resolution(user_name)
    if check_resolution:
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
                called_functions.add_reports_to_subscription(
                    user_name, list_int)
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
    else:
        logging.info(
            f'{user_name} пытался подписаться на получение отчетов. Запрет использования БД')
        await bot.send_message(chat_id, PROHIBITION_PERMISSION)


# Регистрируем хэндлеры
dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(process_command_1, Command(commands='command1'))
dp.message.register(process_command_2, Command(commands='command2'))
dp.message.register(process_command_3, Command(commands='command3'))
dp.message.register(process_command_get_report_for_admin,
                    Command(commands='get_report_for_admin'))
dp.message.register(process_command_add_right_view_reports,
                    Command(commands='add_view'))
dp.message.register(send_echo)


if __name__ == '__main__':
    dp.run_polling(bot)
