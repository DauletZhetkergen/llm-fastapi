import asyncio
import json

import aio_pika
from aio_pika import ExchangeType
from loguru import logger

from config import settings
from llm_process import OpenRouterClient
from utils import send_callback, send_telegram_msg

history = {}

async def receive_tasks():
    connection = await aio_pika.connect_robust("amqp://guest:guest@rabbitmq:5672/")
    async with connection:
        channel = await connection.channel()
        exchange = await channel.declare_exchange(
            "webhook_exchange", ExchangeType.DIRECT, durable=True
        )
        queue = await channel.declare_queue(settings.QUEUE_NAME, durable=True)
        await queue.bind(exchange, routing_key=settings.QUEUE_NAME)
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                message_body = message.body.decode()
                data = json.loads(message_body)
                orc = OpenRouterClient()
                user_ip = data["ip"]
                user_message = data["message"]
                if user_ip not in history:
                    history[user_ip] = []
                history[user_ip].append({"role": "user", "content": user_message})
                llm_returned_text = await orc.send_request(prompt=user_message)
                history[user_ip].append({"role": "assistant", "content": llm_returned_text})

                print(history)


                logger.info("Sending message to TG")
                tg_status_code = await send_telegram_msg(llm_returned_text)
                logger.info("Sending callback")
                logger.info(tg_status_code)
                await send_callback(data["callback_url"],tg_status_code)

        await queue.consume(on_message)

        print("Waiting for tasks...")
        await asyncio.Future()


asyncio.run(receive_tasks())
