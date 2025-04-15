import time
import json

import pika

from processor import FileProcessor


class RabbitMQWorker:
    """
    A worker that consumes messages from a RabbitMQ queue and processes files.
    This worker connects to RabbitMQ, listens for messages on a specified queue,
    and processes the files specified in the messages.
    """

    def __init__(
        self,
        queue_name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        file_path: str,
        ml_host: str,
        ml_port: int,
    ):
        self.queue_name = queue_name
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(username, password)
        self.params = pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=self.credentials
        )
        self.file_path = file_path
        self.connection = None
        self.channel = None
        self.ml_host = ml_host
        self.ml_port = ml_port

    def connect(self):
        """
        Establish a connection to RabbitMQ and declare the queue.
        This method attempts to connect to RabbitMQ and declare the queue.
        If the connection fails, it retries a few times before raising an exception.
        """
        for _ in range(2):
            try:
                self.connection = pika.BlockingConnection(self.params)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name)
                print(f"Connected to RabbitMQ and declared queue: {self.queue_name}")
                return
            except pika.exceptions.AMQPConnectionError:
                print("Retrying connection to RabbitMQ...")
                time.sleep(2)
        raise Exception("Failed to connect to RabbitMQ after retries")

    def callback(self, ch, method, properties, body):
        """
        Callback function to process messages from the RabbitMQ queue.
        This function is called whenever a new message is received on the queue.
        It decodes the message body and calls the FileProcessor to process the file.
        Args:
            ch: The channel object.
            method: The method frame.
            properties: The properties of the message.
            body: The body of the message (file name).
        Raises:
            Exception: If there is an error processing the message.
        Returns:
            None
        """
        try:
            filename = body.decode()
            if not filename:
                print("Invalid message format: 'filename' missing")
                if ch.is_open:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            print(f"Received message for file: {filename}")

            processor = FileProcessor(self.file_path, self.ml_host, self.ml_port)
            processor.process_file(filename)
            if ch.is_open:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError:
            print("Failed to decode message")
            if ch.is_open:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(f"Error processing message: {str(e)}")
            if ch.is_open:
                ch.basic_ack(delivery_tag=method.delivery_tag)

    def start_consuming(self):
        """
        Start consuming messages from the RabbitMQ queue.
        This method sets up the callback function and starts the message loop.
        It will run indefinitely until the connection is closed.
        """
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self.callback, auto_ack=False
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()
