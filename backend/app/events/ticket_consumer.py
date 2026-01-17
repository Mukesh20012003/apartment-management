# backend/app/events/ticket_consumer.py
import json
import logging
import pika

from app.config import settings
from app.events.event_bus import SYNC_EXCHANGE_NAME

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Use the AMQP URL from settings, e.g. amqp://user:pass@rabbitmq:5672/
    params = pika.URLParameters(settings.RABBITMQ_URL)

    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Same exchange as sync publisher
    channel.exchange_declare(
        exchange=SYNC_EXCHANGE_NAME,
        exchange_type="topic",
        durable=True,
    )

    result = channel.queue_declare(queue="ticket_created_queue", durable=True)
    queue_name = result.method.queue

    channel.queue_bind(
        exchange=SYNC_EXCHANGE_NAME,
        queue=queue_name,
        routing_key="ticket.created",
    )

    logger.info("Waiting for ticket.created events...")

    def callback(ch, method, properties, body):
        data = json.loads(body)
        logger.info("Received ticket.created event: %s", data)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()
        connection.close()


if __name__ == "__main__":
    main()
