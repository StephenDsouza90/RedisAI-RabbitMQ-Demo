import time
import pika

from batch_process.processor import FileProcessor


class RabbitMQWorker:
    """
    A worker that consumes messages from a RabbitMQ queue and processes files.
    This worker connects to RabbitMQ, listens for messages on a specified queue,
    and processes the files specified in the messages.
    """
    def __init__(self, queue_name, host, port, username, password, file_path):
        self.queue_name = queue_name
        self.host = host
        self.port = port
        self.credentials = pika.PlainCredentials(username=username, password=password)
        self.params = pika.ConnectionParameters(host=self.host, port=self.port, credentials=self.credentials)
        self.file_path = file_path
        self.connection = None
        self.channel = None

    def connect(self):
        """
        Establish a connection to RabbitMQ and declare the queue.
        This method attempts to connect to RabbitMQ and declare the queue.
        If the connection fails, it retries a few times before raising an exception.
        """
        for _ in range(5):
            try:
                self.connection = pika.BlockingConnection(self.params)
                self.channel = self.connection.channel()
                self.channel.queue_declare(queue=self.queue_name)
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
            processor = FileProcessor(self.file_path)
            processor.process_file(body.decode())
        except Exception as e:
            print(f"Error processing message: {e}")

    def start_consuming(self):
        """
        Start consuming messages from the RabbitMQ queue.
        This method sets up the callback function and starts the message loop.
        It will run indefinitely until the connection is closed.
        """
        self.channel.basic_consume(queue=self.queue_name, on_message_callback=self.callback, auto_ack=True)
        self.channel.start_consuming()


