#!/usr/bin/python

import logging
import random
import threading
import time
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

def handler_404(self):
    self.send_response(404)

def handler_foo(self):
    logging.info("Handling foo...")
    time.sleep(.075 + random.random() * .05)
    self.send_response(200)
    self.end_headers()
    self.wfile.write("Handled foo")

def handler_bar(self):
    logging.info("Handling bar...")
    time.sleep(.15 + random.random() * .1)

    self.send_response(200)
    self.end_headers()
    self.wfile.write("Handled bar")

ROUTES = {
    "/api/foo": handler_foo,
    "/api/bar": handler_bar,
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ROUTES.get(self.path, handler_404)(self)

class MultiThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class Server(threading.Thread):
    def run(self):
        httpd = MultiThreadedHTTPServer(('', 12345), Handler)
        httpd.serve_forever()

def background_task():
    logging.info("Starting background task loop...")
    while True:
        logging.info("Performing background task...")
        # Simulate a random duration that the background task needs to be completed.
        time.sleep(1 + random.random() * 0.5)

        # Simulate the background task either succeeding or failing (with a 30% probability).
        if random.random() > 0.3:
            logging.info("Background task completed successfully.")
        else:
            logging.warn("Background task failed.")

        time.sleep(5)

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    s = Server()
    s.daemon = True
    s.start()
    background_task()
