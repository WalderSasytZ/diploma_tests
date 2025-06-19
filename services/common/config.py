import asyncpg
import aio_pika

intensity = 0.2
message_count = 1000
user_num = 100
speed = 1


async def database_connection_init():
    return await asyncpg.connect(user="admin", password="admin", database="postgres", host="postgres", port=5432)


connection = None
channel = None


async def get_connection():
    global connection
    if connection is None or connection.is_closed:
        connection = await aio_pika.connect_robust("amqp://admin:admin@rabbitmq:5672/")
    return connection


async def get_channel():
    global connection
    global channel
    if channel is None or channel.is_closed:
        connection = await get_connection()
        channel = await connection.channel()
    return channel
