from socket import socket, SOL_SOCKET, SO_REUSEADDR
from socket_base import Socket
import errno
from threading import Thread
import logging


class Server(Socket):

    def __init__(self, IP='127.0.0.1', port=11419, skt: socket = None,
                 header=12, format="utf-8") -> None:
        super().__init__(IP, port, skt, header, format)

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
            conn, addr = self.socket.accept()
            logging.info(f"Connection from {addr} accepted")
            Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn: socket, addr):
        """
            Handles a client connection
        """
        pass
