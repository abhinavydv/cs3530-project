from socket import socket, SOCK_STREAM
from typing import Tuple


class Socket(object):
    """
        An extension on socket.io to atomize sending and receiving all data
        TODO: Encrypt all communication
    """

    def __init__(self, IP='127.0.0.1', port=11419, skt: socket = None,
                 header=12, format="utf-8") -> None:
        """
            If `skt` is None a new socket object is created
        """
        if skt is not None:
            self.socket = skt
        else:
            self.socket = self.new_socket()
        self.IP = IP
        self.port = port
        self.HEADER = header
        self.FORMAT = format
        self.addr = (IP, port)
        self.running = False

    def connect(self, addr: Tuple[str, int] = None, conn: socket = None):
        """
            connects to the server
        """
        if conn is None:
            conn = self.socket
        if addr is None:
            addr = self.addr
        conn.connect(self.addr)

    def send_data(self, data: bytes|str, conn: socket = None):
        """
            sends all data over `conn` or `self.socket`.
            Blocks untill all data is sent or an error in encountered
        """

        if isinstance(data, str):
            data = data.encode(self.FORMAT)

        if not isinstance(data, bytes):
            raise TypeError(f"Expected bytes or str, got {type(data)}")

        if conn is None:
            conn = self.socket
        ln = str(len(data)).encode(self.FORMAT)

        # send length of data
        conn.sendall(ln + ' '.encode(self.FORMAT)*(self.HEADER-len(ln)))
        conn.sendall(data)  # send data

    def recv_data(self, conn: socket = None) -> bytes:
        """
            receives all data from `conn` or `self.socket`.
            Blocks untill all data is sent or an error in encountered
        """
        if conn is None:
            conn = self.socket
        ln = data = b''
        t = self.HEADER

        # first get length of data
        while t:
            temp = conn.recv(t)
            if not temp:
                return b''
            ln += temp
            t -= len(temp)
        ln = int(ln)

        # then get data
        while ln:
            temp = conn.recv(ln)
            if not temp:
                return b''
            ln -= len(temp)
            data += temp

        return data
