from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
import called_functions
import config

# Вместо BOT TOKEN HERE нужно вставить токен вашего бота, полученный у @BotFather
BOT_TOKEN = config.BOT_TOKEN

# Создаем объекты бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# Этот хэндлер будет срабатывать на команду "/start"
async def process_start_command(message: Message):
    user_name = message.chat.username
    chat_id = message.chat.id
    await message.answer(f'Привет, {user_name}!\nМеня зовут Эхо-бот!\nНапиши мне что-нибудь.\
        \nА пока посмотри котиков.')
    url = called_functions.get_image_cat()
    await bot.send_photo(chat_id, url)


# Этот хэндлер будет срабатывать на команду "/help
async def process_help_command(message: Message):
    await message.answer(
        'Напиши мне что-нибудь и в ответ '
        'я пришлю тебе твое сообщение'
    )
    

# Этот хэндлер будет срабатывать на команду "/command1"
async def process_command_1(message: Message):
    await message.answer('Тест. Получены доступные для подписки отчеты.')
    

# Этот хэндлер будет срабатывать на команду "/command2"
async def process_command_2(message: Message):
    await message.answer('Тест. Получены отчеты по подписке.')
    

# Этот хэндлер будет срабатывать на команду "/command3"
async def process_command_3(message: Message):
    await message.answer('Тест. Вы отписались от получения отчетов по подписке.')


# Этот хэндлер будет срабатывать на любые ваши текстовые сообщения,
# кроме команд "/start" и "/help"
async def send_echo(message: Message):
    await message.reply(text=message.text)
    

# Регистрируем хэндлеры
dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(process_command_1, Command(commands='command1'))
dp.message.register(process_command_2, Command(commands='command2'))
dp.message.register(process_command_3, Command(commands='command3'))
dp.message.register(send_echo)


if __name__ == '__main__':
    dp.run_polling(bot)