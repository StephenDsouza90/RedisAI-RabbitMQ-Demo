from file_process.worker import RabbitMQWorker
from file_process.api import HealthCheckAPI

# Start the health check API
health_check_api = HealthCheckAPI()
health_check_api.start()

# Start the RabbitMQ worker
worker = RabbitMQWorker(queue_name="file_queue")
worker.connect()
worker.start_consuming()
