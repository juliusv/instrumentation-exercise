#!/usr/bin/python3

import logging
import random
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from prometheus_client import (
    Histogram,
    Counter,
    MetricsHandler,
    generate_latest,
    REGISTRY,
    CONTENT_TYPE_LATEST,
)


def handler_404(self):
    self.send_response(404)
    self.end_headers()


def handler_foo(self):
    logging.info("Handling foo...")
    time.sleep(0.075 + random.random() * 0.05)
    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Handled foo")


def handler_bar(self):
    logging.info("Handling bar...")
    time.sleep(0.15 + random.random() * 0.1)

    self.send_response(200)
    self.end_headers()
    self.wfile.write(b"Handled bar")


def handler_metrics(self):
    try:
        output = generate_latest(REGISTRY)
    except:
        self.send_error(500, "error generating metrics output")
        raise
    self.send_response(200)
    self.send_header("Content-Type", CONTENT_TYPE_LATEST)
    self.end_headers()
    self.wfile.write(output)


ROUTES = {
    "/api/foo": handler_foo,
    "/api/bar": handler_bar,
    "/metrics": handler_metrics,
}


class Handler(BaseHTTPRequestHandler):
    request_durations = Histogram(
        "some_api_http_request_duration_seconds",
        "A histogram of the demo API request durations in seconds.",
        ["path"],
        buckets=(0.05, 0.075, 0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.250, 0.275),
    )

    def do_GET(self):
        start = time.time()

        ROUTES.get(self.path, handler_404)(self)

        self.request_durations.labels(path=self.path).observe(time.time() - start)


class MultiThreadedHTTPServer(ThreadingHTTPServer):
    pass


class Server(threading.Thread):
    def run(self):
        httpd = MultiThreadedHTTPServer(("", 12345), Handler)
        httpd.serve_forever()


def background_task():
    total_count = Counter(
        "background_task_runs_total",
        "The total number of background task runs.",
    )
    failure_count = Counter(
        "background_task_failures_total",
        "The total number of background task failures.",
    )

    logging.info("Starting background task loop...")
    while True:
        logging.info("Performing background task...")
        # Simulate a random duration that the background task needs to be completed.
        time.sleep(1 + random.random() * 0.5)

        # Simulate the background task either succeeding or failing (with a 30% probability).
        if random.random() > 0.3:
            logging.info("Background task completed successfully.")
        else:
            failure_count.inc()
            logging.warning("Background task failed.")
        total_count.inc()

        time.sleep(5)


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    s = Server()
    s.daemon = True
    s.start()
    background_task()
