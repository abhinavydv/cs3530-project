from socket import socket
from socket_base import Socket


class Client(Socket):

    def __init__(self, IP='127.0.0.1', port=11419, skt: socket = None,
                 header=12, format="utf-8") -> None:
        super().__init__(IP, port, skt, header, format)

    def start(self):
        """
            Starts the client
        """
        self.running = True
        self.connect()
        self.run()
        
    def run(self):
        pass
    
    def send_edit(self, diff: str):
        """
            Sends the edits to all peers using IGMP
        """

    
