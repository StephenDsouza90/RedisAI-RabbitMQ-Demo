import os

from worker import RabbitMQWorker


def main():
    # Load environment variables for RabbitMQ
    host = os.getenv("RABBITMQ_HOST")
    port = os.getenv("RABBITMQ_PORT")
    username = os.getenv("RABBITMQ_USER")
    password = os.getenv("RABBITMQ_PASSWORD")
    queue_name = os.getenv("RABBITMQ_QUEUE")
    file_path = os.getenv("FILE_PATH")

    # ML env variables
    ml_host = os.getenv("ML_HOST")
    ml_port = os.getenv("ML_PORT")

    # Start the RabbitMQ worker
    worker = RabbitMQWorker(
        queue_name, host, port, username, password, file_path, ml_host, ml_port
    )
    worker.connect()
    worker.start_consuming()


if __name__ == "__main__":
    print("Starting the application...")
    main()
