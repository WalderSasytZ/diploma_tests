import asyncio
import logging
import sys
import signal
from common import config, database


async def main():
    await asyncio.sleep(3600)


def handle_exit(signum, frame):
    config.channel.close()
    config.connection.close()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, handle_exit)  # Для корректной остановки контейнера
    asyncio.run(main())
