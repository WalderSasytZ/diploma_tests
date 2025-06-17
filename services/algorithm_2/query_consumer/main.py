import asyncio
import logging
import signal
import sys
import json

from common import config, database


async def consumer():
    await asyncio.sleep(10)
    channel = await config.get_channel()
    queue = await channel.declare_queue(name="Q_M", durable=True, passive=False)

    while True:
        await asyncio.sleep(0.2 / config.speed)

        while True:
            await asyncio.sleep(0.035 / config.speed)
            data = await queue.get(no_ack=True, fail=False)
            if not data:
                break
            await database.send_mail(json.loads(data.body.decode()), 2)


def handle_exit(signum, frame):
    config.channel.close()
    config.connection.close()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, handle_exit)  # Для корректной остановки контейнера
    asyncio.run(consumer())
