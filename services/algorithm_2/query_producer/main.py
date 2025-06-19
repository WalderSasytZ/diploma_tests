import asyncio
import logging
import signal
import sys
import json
from datetime import datetime

from common import config, database
from aio_pika import Message


async def producer():
    await asyncio.sleep(5)
    channel = await config.get_channel()
    await channel.declare_queue(name="queue", durable=True, passive=False)
    logging.info("producer started")

    while True:
        mails = await database.get_mails(algorithm=2, get_one_message=True)
        if not mails:
            await asyncio.sleep(0.05 / config.speed)
            continue

        for mail in mails:
            await channel.default_exchange.publish(
                message=Message(body=json.dumps({
                    'message_id': mail['message_id'],
                    'user_id': mail['user_id'],
                    'arrived': datetime.strftime(mail['arrived'], "%Y-%m-%d %H:%M:%S.%f")
                }).encode()),
                routing_key='queue'
            )
        await database.delete_messages([mails[0]["message_id"]], algorithm=2)
        await asyncio.sleep(3.2 / config.speed)


def handle_exit(signum, frame):
    config.channel.close()
    config.connection.close()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, handle_exit)
    asyncio.run(producer())
