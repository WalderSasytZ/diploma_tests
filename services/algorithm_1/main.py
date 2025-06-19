import asyncio
import logging
import sys
import signal
from datetime import datetime
from common import config, database


async def main():
    await asyncio.sleep(5)
    logging.info("algorithm_1 started")

    while True:
        mails = await database.get_mails(algorithm=1, get_one_message=False)
        await database.clear_sets()
        if not mails:
            await asyncio.sleep(0.05 / config.speed)
            continue

        used_messages = []
        mails = sorted(mails, key=lambda x: datetime.now() - x['arrived'], reverse=True)
        mails_to_send = []

        global_delta = await database.get_global_delta()
        users_delta = await database.get_users_delta()

        for mail in mails:
            if mail['message_id'] not in used_messages:
                used_messages.append(mail['message_id'])
            user_count = next((
                user_delta['cnt']
                for user_delta in users_delta
                if user_delta['user_id'] == mail['user_id']
            ), 0)
            user_mails_to_send = len([
                mail_to_send
                for mail_to_send in mails_to_send
                if mail['user_id'] == mail_to_send['user_id']
            ])
            if global_delta + len(mails_to_send) < 30 and user_count + user_mails_to_send < 20:
                mails_to_send.append(mail)
                await database.send_mail(mail, algorithm=1)

        await database.delete_messages(used_messages, algorithm=1)


def handle_exit(signum, frame):
    config.channel.close()
    config.connection.close()
    sys.exit(0)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGTERM, handle_exit)  # Для корректной остановки контейнера
    asyncio.run(main())
