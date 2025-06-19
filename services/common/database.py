from datetime import datetime, timedelta
from common.config import database_connection_init, speed


async def init_database():
    conn = await database_connection_init()
    await conn.execute('''
        DROP TABLE IF EXISTS Q_M;
        DROP TABLE IF EXISTS Q_global;
        DROP TABLE IF EXISTS Q_user;
        DROP TABLE IF EXISTS results;

        CREATE TABLE IF NOT EXISTS Q_M (
            message_id  INT        NOT NULL,
            user_ids    TEXT       NOT NULL,
            arrived     TIMESTAMP  NOT NULL,
            algorithm   INT        NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Q_global (
            message_id  INT        NOT NULL,
            user_id     INT        NOT NULL,
            sent        TIMESTAMP  NOT NULL
        );

        CREATE TABLE IF NOT EXISTS Q_user (
            message_id  INT        NOT NULL,
            user_id     INT        NOT NULL,
            sent        TIMESTAMP  NOT NULL
        );

        CREATE TABLE IF NOT EXISTS results (
            message_id  INT        NOT NULL,
            user_id     INT        NOT NULL,
            arrived     TIMESTAMP  NOT NULL,
            sent        TIMESTAMP  NOT NULL,
            algorithm   INT        NOT NULL
        );
    ''')
    await conn.close()


async def insert_message(message_id, users):
    conn = await database_connection_init()
    await conn.executemany(f'''
        INSERT INTO Q_M (
            message_id,
            user_ids,
            arrived,
            algorithm
        ) VALUES ($1, $2, $3, $4)
    ''', ((message_id, '-'.join(users), datetime.now(), 1),
          (message_id, '-'.join(users), datetime.now(), 2)))
    await conn.close()


async def get_mails(algorithm, get_one_message):
    conn = await database_connection_init()
    mails = []
    messages = await conn.fetch(f'''
        SELECT *
          FROM Q_M
         WHERE algorithm = $1 {"ORDER BY arrived ASC LIMIT 1" if get_one_message else ""}
    ''', algorithm)
    for message in messages:
        for user_id in message["user_ids"].split('-'):
            mails.append({
                "message_id": message["message_id"],
                "user_id": int(user_id),
                "arrived": message["arrived"],
                "algorithm": message["algorithm"]
            })
    await conn.close()
    return mails


async def delete_messages(message_ids, algorithm):
    conn = await database_connection_init()
    await conn.executemany(f'''
        DELETE FROM Q_M
         WHERE algorithm = $1
           AND message_id = $2
    ''', tuple([(algorithm, message_id) for message_id in message_ids]))
    await conn.close()


async def send_mail(mail, algorithm):
    conn = await database_connection_init()
    now = datetime.now()
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
            mail['arrived'] if isinstance(mail['arrived'], datetime) else
            datetime.strptime(mail['arrived'], "%Y-%m-%d %H:%M:%S.%f"),
            now,
            algorithm
    )

    if algorithm == 1:
        await conn.execute(f'''
            INSERT INTO Q_global (
                message_id,
                user_id,
                sent
            ) VALUES ($1, $2, $3)
        ''', mail['message_id'],
             mail['user_id'],
             now
        )
        await conn.execute(f'''
            INSERT INTO Q_user (
                message_id,
                user_id,
                sent
            ) VALUES ($1, $2, $3)
        ''', mail['message_id'],
             mail['user_id'],
             now
        )

    await conn.close()


async def clear_sets():
    conn = await database_connection_init()
    now = datetime.now()

    await conn.execute('''
        DELETE FROM Q_global
         WHERE sent < $1
    ''', now - timedelta(seconds=(1 / speed)))
    await conn.execute('''
        DELETE FROM Q_user
         WHERE sent < $1
    ''', now - timedelta(seconds=(60 / speed)))

    await conn.close()


async def get_global_delta():
    conn = await database_connection_init()
    delta = await conn.fetchval('''SELECT COUNT(*) FROM Q_global''')
    await conn.close()
    return delta


async def get_users_delta():
    conn = await database_connection_init()
    deltas = await conn.fetch('''
        SELECT user_id,
               COUNT(*) as cnt
          FROM Q_user
         GROUP BY user_id''')
    await conn.close()
    return deltas
