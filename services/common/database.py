from datetime import datetime
from common.config import database_connection_init


async def insert_message(message_id, users):
    conn = await database_connection_init()
    now = datetime.now()
    await conn.executemany(f'''
        INSERT INTO Q_M (
            message_id,
            user_id,
            arrived,
            algorithm
        ) VALUES ($1, $2, $3, $4)
    ''', tuple([(message_id, user_id, now, 1) for user_id in users] +
               [(message_id, user_id, now, 2) for user_id in users]))
    await conn.close()


async def get_mails(algorithm):
    conn = await database_connection_init()
    mails = await conn.fetch(f'''
        SELECT *
          FROM Q_M
         WHERE algorithm = $1
    ''', algorithm)
    await conn.close()
    return mails


async def delete_mails(mails, algorithm):
    conn = await database_connection_init()
    await conn.executemany('''
        DELETE FROM Q_M
         WHERE algorithm = $1
           AND message_id = $2
           AND user_id = $3
    ''', algorithm, tuple([(mail['message_id'], mail['user_id']) for mail in mails]))
    await conn.close()


async def send_mail(mail, algorithm):
    conn = await database_connection_init()
    await conn.execute(f'''
        INSERT INTO results (
            message_id,
            user_id,
            arrived,
            sent,
            algorithm    
        ) VALUES ($1, $2, $3, $4, $5)
    ''',    mail['message_id'],
            mail['user_id'],
            mail['arrived'],
            datetime.now(),
            algorithm
    )
    await conn.close()
