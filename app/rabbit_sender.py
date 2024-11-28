import json

from aio_pika import connect_robust, Message, ExchangeType
from loguru import logger

from config import settings


class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):

        self.connection = await connect_robust(settings.RABBITMQ_URL)
        self.channel = await self.connection.channel()
        self.exchange = await self.channel.declare_exchange(
            "webhook_exchange", ExchangeType.DIRECT, durable=True
        )
        logger.info("RabbitMQ connected")

    async def publish_message(self, queue_name: str, message_body: dict):
        logger.info("Inserting to queue")
        await self.channel.declare_queue(queue_name, durable=True)
        message = Message(body=json.dumps(message_body).encode())
        await self.exchange.publish(message, routing_key=queue_name)
        logger.info("Message published")

    async def close(self):
        if self.connection:
            await self.connection.close()
        logger.info("Closed connection")
