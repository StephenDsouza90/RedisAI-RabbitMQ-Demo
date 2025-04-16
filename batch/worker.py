"""
RabbitMQ Worker for File Processing
This module defines a RabbitMQWorker class that connects to a RabbitMQ server,
consumes messages from a specified queue, and processes files based on the received messages.
"""

import time
import json

import pika

from processor import FileProcessor


class RabbitMQWorker:
    """
    A worker that consumes messages from a RabbitMQ queue and processes files.

    This worker connects to RabbitMQ, listens for messages on a specified queue,
    and processes the files specified in the messages using the FileProcessor.
    """

    def __init__(
        self,
        queue_name: str,
        host: str,
        port: int,
        username: str,
        password: str,
        file_path: str,
        ml_url: str,
    ):
        """
        Initialize the RabbitMQWorker with connection and processing details.

        Args:
            queue_name (str): Name of the RabbitMQ queue to consume messages from.
            host (str): RabbitMQ server hostname or IP address.
            port (int): RabbitMQ server port.
            username (str): Username for RabbitMQ authentication.
            password (str): Password for RabbitMQ authentication.
            file_path (str): Path to the directory where files are stored.
            ml_url (str): URL of the machine learning service for processing files.
        """
        self.queue_name = queue_name
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(username, password)
        self.connection_params = pika.ConnectionParameters(
            host=self.host, port=self.port, credentials=self.credentials
        )
        self.file_path = file_path
        self.connection = None
        self.channel = None
        self.ml_url = ml_url

    def connect(self, max_retries: int = 2):
        """
        Establish a connection to RabbitMQ and declare the queue.

        This method attempts to connect to RabbitMQ and declare the queue.
        If the connection fails, it retries a few times before raising an exception.

        Raises:
            Exception: If the connection to RabbitMQ fails after retries.
        """
        for attempt in range(max_retries):
            try:
                self.connection = pika.BlockingConnection(self.connection_params)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name)
                print(f"Connected to RabbitMQ and declared queue: {self.queue_name}")
                return
            except pika.exceptions.AMQPConnectionError:
                print(f"Connection attempt {attempt + 1} failed. Retrying...")
                time.sleep(2)
        raise Exception("Failed to connect to RabbitMQ after multiple retries")

    def _process_message(self, channel, method, body):
        """
        Process a single message from the RabbitMQ queue.

        Args:
            channel: The channel object.
            method: The method frame containing delivery information.
            body: The body of the message (file name).

        Raises:
            Exception: If there is an error processing the message.
        """
        try:
            filename = body.decode()
            if not filename:
                print("Invalid message format: 'filename' missing")
                return

            print(f"Processing file: {filename}")
            processor = FileProcessor(self.file_path, self.ml_url)
            processor.process_file(filename)

        except json.JSONDecodeError:
            print("Failed to decode message body as JSON")
        except Exception as e:
            print(f"Error processing file: {str(e)}")
        finally:
            if channel.is_open:
                channel.basic_ack(delivery_tag=method.delivery_tag)

    def _message_callback(self, channel, method, properties, body):
        """
        Callback function to handle messages from the RabbitMQ queue.

        Args:
            channel: The channel object.
            method: The method frame containing delivery information.
            properties: The properties of the message.
            body: The body of the message (file name).
        """
        print(f"Received message: {body}")
        self._process_message(channel, method, body)

    def start_consuming(self):
        """
        Start consuming messages from the RabbitMQ queue.

        This method sets up the callback function and starts the message loop.
        It will run indefinitely until the connection is closed.
        """
        if not self.channel:
            raise Exception("RabbitMQ channel is not initialized. Call 'connect' first.")

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue=self.queue_name, on_message_callback=self._message_callback, auto_ack=False
        )
        print(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()
