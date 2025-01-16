
# for i in range(1, 6):
#     email_addresses.append(f"user{i}@example.com")

# print(email_addresses)

email_addresses = [
    'user1@example.com', 'user2@example.com',
    'user3@example.com', 'user4@example.com', 'user5@example.com'
]

message_text = "Статус заказа изменен"

message = {
    "email": email_addresses,
    "message": message_text
}

message = {
    "email": [
        'user1@example.com', 'user2@example.com',
        'user3@example.com', 'user4@example.com', 'user5@example.com'
    ],
    "message": "Статус заказа изменен"
}
main(message)

# s = smtplib.SMTP('smtp.mail.ru', 25)
# s.starttls()
# s.login(from_email, password)
# s.sendmail(from_email, dest, body["message"])
# s.quit()
# print(dest, body['message'])

# producer

from pika import ConnectionParameters, PlainCredentials, BlockingConnection

connection_params = ConnectionParameters(
    host="localhost",
    port=5672,
    credentials=PlainCredentials("rmuser", "rmpassword"),
)


async def main(message: EmailVal):
    async with BlockingConnection(connection_params) as conn:
        async with conn.channel() as ch:
            ch.queue_declare(queue="messages")

            ch.basic_publish(
                exchange="",
                routing_key="messages",
                body=json.dumps(message.dict())
            )
            print("message sent")






# consumer
from pika import ConnectionParameters, PlainCredentials, BlockingConnection
import smtplib
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


connection_params = ConnectionParameters(
    host="localhost",
    port=5672,
    credentials=PlainCredentials("rmuser", "rmpassword"),
)


def proces_message(ch, method, properties, body):
    body = json.loads(body)
    print(body)
    for dest in body["email_list"]:
        msg = MIMEMultipart()
        msg["From"] = from_email
        msg['To'] = dest
        msg["Subject"] = Header('Тема сообщения', 'utf-8')
        msg["Date"] = formatdate(localtime=True)
        msg.attach(MIMEText(body['message'], 'html', 'utf-8'))

        smtp = smtplib.SMTP(smtp_server, smtp_port)
        smtp.starttls()
        smtp.ehlo()
        smtp.login(from_email, password)
        smtp.sendmail(from_email, dest, msg.as_string())
        smtp.quit()
        # [("gmail.com", 587), ("mail.ru", 25), ("yandex.ru", 465)]
    ch.basic_ack(delivery_tag=method.delivery_tag)




def main():
    with BlockingConnection(connection_params) as conn:
        with conn.channel() as ch:
            ch.queue_declare(queue="messages")

            ch.basic_consume(
                queue="messages",
                on_message_callback=proces_message
            )
            print("--- Жду сообщений ... ---")
            ch.start_consuming()


if __name__ == '__main__':
    if not from_email:
        print("Ошибка: переменная окружения FROM_EMAIL не установлена.")
        exit(1)
    if not password:
        print("Ошибка: переменная окружения PASSWORD не установлена.")
        exit(1)
    main()
