from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from configparser import ConfigParser

config = ConfigParser()
config.read("bot.ini")

bot = Bot(token=config["Bot"]["token"])
dispatcher = Dispatcher(bot, storage=MemoryStorage())
