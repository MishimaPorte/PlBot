from tortoise import Tortoise
from configparser import ConfigParser
from bot import dispatcher
import asyncio
import commands as commands

config = ConfigParser()
config.read("configs/bot.ini")

tort = {
    "connections": {
        "default": f'{config["Database"]["type"]}://{config["Database"]["user"]}:{config["Database"]["password"]}@{config["Database"]["host"]}:{config["Database"]["port"]}/{config["Database"]["dbname"]}'
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init():
    await Tortoise.init(tort)
    await Tortoise.generate_schemas()

    await dispatcher.start_polling(debug=True)


def main():
    asyncio.run(init())


if __name__ == "__main__":
    main()
