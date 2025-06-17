import asyncio
import logging
import random
import sys
import signal
from common import config, database


# В худшем случае среднее время работы О(N*logN), N=config.user_num
def generate_user_list():
    user_count = random.randint(1, config.user_num)
    user_list = []
    while len(user_list) < user_count:
        user_id = random.randint(1, config.user_num)
        if user_id not in user_list:
            user_list.append(user_id)
    return user_list


async def main():
    await asyncio.sleep(15)
    for message_id in range(config.message_count):
        await asyncio.sleep(random.expovariate(config.intensity * config.speed))
        await database.insert_message(message_id, generate_user_list())


def handle_exit(signum, frame):
    config.channel.close()
    config.connection.close()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, handle_exit)  # Для корректной остановки контейнера
    asyncio.run(main())
