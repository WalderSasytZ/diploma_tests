import asyncio
import logging
import signal
import sys
import json

from common import config, database


async def consumer():
    await asyncio.sleep(5)
    channel = await config.get_channel()
    queue = await channel.declare_queue(name="queue", durable=True, passive=False)
    logging.info("consumer started")

    while True:
        await asyncio.sleep(0.035 / config.speed)
        data = await queue.get(no_ack=False, fail=False)
        if data:
            await database.send_mail(json.loads(data.body.decode()), 2)
            await data.ack()


def handle_exit(signum, frame):
    config.channel.close()
    config.connection.close()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, handle_exit)  # Для корректной остановки контейнера
    asyncio.run(consumer())
