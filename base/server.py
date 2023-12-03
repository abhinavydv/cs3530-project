from socket import socket, SOL_SOCKET, SO_REUSEADDR
from base.socket_base import Socket
import errno
from threading import Thread
import logging
import random


root = logging.getLogger()
root.setLevel(logging.INFO)


class Server(Socket):

    def __init__(self, control, IP=None, port=None, skt: socket = None,
                 header=12, format="utf-8") -> None:
        if IP is None:
            IP = self.get_ip()
        if port is None:
            port = random.randint(10000, 65535)
        super().__init__(IP, port, skt, header, format)

        self.control = control

    def start(self):
        """
            Start the server.
        """
        self.running = True

        # make the address reusable
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        try:
            self.socket.bind(self.addr)
        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                logging.fatal(f"Address {self.addr} already in use")
                return
        self.socket.listen()
        logging.info(f"Server started listening on {self.addr}")
        self.run()

    def run(self):
        """
            Accepts connections and starts a new thread for each connection
        """
        while self.running:
            logging.info("Waiting for connection...")
            conn, addr = self.socket.accept()
            logging.info(f"Connection from {addr} accepted")
            Thread(target=self.control.handle_client, args=(conn, addr)).start()
            
    def stop(self):
        """
            Stops the server
        """
        self.running = False
        self.socket.close()
        logging.info("Server stopped")
