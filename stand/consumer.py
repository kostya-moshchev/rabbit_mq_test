from aio_pika import connect_robust, IncomingMessage
import aiosmtplib
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formatdate
import json
import os
from dotenv import load_dotenv

load_dotenv()

from_email = os.getenv('FROM_EMAIL')
password = os.getenv('PASSWORD')
smtp_server = "smtp.mail.ru"
smtp_port = 25
# [("gmail.com", 587), ("mail.ru", 25), ("yandex.ru", 465)]


async def send_email(to_email, message_body):
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg['To'] = to_email
    msg["Subject"] = Header('Тема сообщения', 'utf-8')
    msg["Date"] = formatdate(localtime=True)
    msg.attach(MIMEText(message_body, 'plain', 'utf-8'))
    await aiosmtplib.send(msg,
                          hostname=smtp_server,
                          port=smtp_port,
                          username=from_email,
                          password=password)


async def process_message(message: IncomingMessage):
    async with message.process():
        body = json.loads(message.body.decode())
        print(body)

        email_tasks = [
            send_email(dest, body['message']) for dest in body["email_list"]
        ]
        await asyncio.gather(*email_tasks)
    # message.ch.basic_ack(delivery_tag=method.delivery_tag)


async def main():
    connection = await connect_robust(
         "amqp://rmuser:rmpassword@localhost:5672/",
    )
    queue_name = "messages"
    channel = await connection.channel()
    print('--- Жду сообщений... ---')
    await channel.set_qos(prefetch_count=100)
    queue = await channel.declare_queue(queue_name, auto_delete=False)
    await queue.consume(process_message)
    try:
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == '__main__':
    asyncio.run(main())
