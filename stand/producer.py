from aio_pika import Message, connect_robust
import uvicorn
import json
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
import os
from dotenv import load_dotenv

load_dotenv()

user = os.getenv('USER')
password = os.getenv('PASSWORD_RMQ')

app = FastAPI()


class EmailVal(BaseModel):
    email_list: list[EmailStr]
    message: str


@app.post("/send_to_mail")
async def send_email(message: EmailVal):
    await main(message)
    return {"ok": True, "msg": "kaif"}


async def main(message: EmailVal) -> None:
    connection = await connect_robust(
        "amqp://rmuser:rmpassword@localhost:5672/",
    )
    async with connection:
        channel = await connection.channel()

        await channel.declare_queue("messages")

        await channel.default_exchange.publish(
            Message(body=json.dumps(message.dict()).encode(),),
            routing_key="messages"
        )
        print("message sent")


if __name__ == '__main__':
    uvicorn.run("producer:app", reload=True)
