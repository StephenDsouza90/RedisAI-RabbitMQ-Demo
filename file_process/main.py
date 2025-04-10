import os

from file_process.worker import RabbitMQWorker
from file_process.api import HealthCheckAPI

def main():
    try:
        # Load environment variables for the API
        api_host = os.getenv("API_HOST")
        api_port = os.getenv("API_PORT")

        # Load environment variables for RabbitMQ
        host = os.getenv("RABBITMQ_HOST")
        port = os.getenv("RABBITMQ_PORT")
        username = os.getenv("RABBITMQ_USER")
        password = os.getenv("RABBITMQ_PASSWORD")
        queue_name = os.getenv("RABBITMQ_QUEUE")
        file_path = os.getenv("FILE_PATH")

        # Start the health check API
        health_check_api = HealthCheckAPI(api_host, api_port)
        health_check_api.start()

        # Start the RabbitMQ worker
        worker = RabbitMQWorker(queue_name, host, port, username, password, file_path)
        worker.connect()
        worker.start_consuming()
    except Exception as e:
        print(f"An error occurred: {e}")



if __name__ == "__main__":
    main()