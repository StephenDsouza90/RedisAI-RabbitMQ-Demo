import threading

from flask import Flask, jsonify


class HealthCheckAPI:
    """
    A simple health check API using Flask.
    This API provides a single endpoint to check the health of the service.
    """
    def __init__(self, host="0.0.0.0", port=5000):
        self.app = Flask(__name__)
        self.host = host
        self.port = port
        self._setup_routes()

    def _setup_routes(self):
        """
        Set up the health check route.
        This route returns a JSON response indicating the health status of the service.
        """
        @self.app.route("/health", methods=["GET"])
        def health_check():
            return jsonify({"status": "healthy"}), 200

    def start(self):
        """
        Start the Flask application in a separate thread.
        This allows the health check API to run concurrently with other processes.
        """
        threading.Thread(
            target=self.app.run,
            kwargs={"host": self.host, "port": self.port, "debug": False, "use_reloader": False},
            daemon=True
        ).start()

