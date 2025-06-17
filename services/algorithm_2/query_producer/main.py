import asyncio
import logging
import signal
import sys
import json

from common import config, database
from aio_pika import Message


async def producer():
    await asyncio.sleep(10)
    channel = await config.get_channel()
    await channel.declare_queue(name="Q_M", durable=True, passive=False)

    while True:
        await asyncio.sleep(0.2 / config.speed)
        mails = await database.get_mails(algorithm=2)
        if not mails:
            continue

        for mail in mails:
            await channel.default_exchange.publish(
                message=Message(body=json.dumps({
                    'message_id': mail['message_id'],
                    'user_id': mail['user_id'],
                    'arrived': mail['arrived']
                }).encode()),
                routing_key='Q_M'
            )
        await database.delete_mails(mails, algorithm=2)


def handle_exit(signum, frame):
    config.channel.close()
    config.connection.close()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, handle_exit)
    asyncio.run(producer())
